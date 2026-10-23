// ============================================================================
// cnmod_hook.dll - Faza 1.6: diagnostyczne hooki (MinHook) dla CN.PLMOD.exe
//
// Cel: READ-ONLY obserwacja sciezki produkcji - rozstrzygniecie hipotezy:
//   A) produkcja idzie przez FUN_00473461 (unit tick, case38/case39)
//   B) produkcja idzie przez dyspozytor 0x46BAD7 -> handler zdarzen
// Log tez odpowiada, czy job 56 (smolarz) trafia do handlera produkcji
// (patch 614 w EtapC przekierowuje >47 -> 0x46BDC1 -> FUN_00473695).
//
// Podzial pracy z EtapC.dll:
//   - EtapC  = patche danych/limitow tabel w binarce (bez zmian)
//   - cnmod_hook = hooki zachowan przez MinHook (bez patchy kodu)
//
// Budowanie: cnmod_hook\build.bat (MinGW i686 + MinHook - jak etapc\build.bat)
// Injector:  modlauncher.exe wstrzykuje obie DLL (EtapC + cnmod_hook)
// Log:       logs\cnmod_hook.log
// ============================================================================

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstdarg>
#include <cstring>
#include <MinHook.h>
#include "cnmod_hook.h"

// ============================================================================
// Adresy VA (ImageBase 0x400000) - potwierdzone deasemblerem 2026-10-19
// ============================================================================

// Sygnatury (ustalone z prologow i wywolan):
//   unit_tick  0x473461: thiscall(void* unit, int32_t delta)   - 1 arg ze stacka
//   dispatcher 0x46BAD7: thiscall(void* unit)                  - 0 argow
//   potter     0x46D53A: thiscall(void* unit)                  - 0 argow
//   case>47    0x473695: thiscall(void* unit)                  - 0 argow
//                              (cel przekierowania patcha 614 z 0x46BDC1)
//   find_owner 0x43267F: thiscall(void* building, uint32 key)  - ret 4, zwraca
//                              wsk. na owner entry lub NULL (→ AV na 0x4734C6!)
//   stock_add  0x44B910: thiscall(void* stockobj, int good, int qty) - ret 8
//
// Uwaga ABI: thiscall (this w ECX, argi na stacku) == fastcall z dodatkowym
// paramorem-pelniaczem w EDX. Detour i wywolanie oryginalu przez wskazniki
// __fastcall sa wiec ABI-zgodne (EDX przepuszczamy bez zmian do oryginalu).

static const uintptr_t VA_UNIT_TICK  = 0x473461;
static const uintptr_t VA_DISPATCHER = 0x46BAD7;
static const uintptr_t VA_POTTER     = 0x46D53A;
static const uintptr_t VA_CASE46BDC1 = 0x473695;
static const uintptr_t VA_FIND_OWNER = 0x43267F;
static const uintptr_t VA_STOCK_ADD  = 0x44B910;

// Bramki na sciezce FUN_00473695 (rozklad 2026-10-19) - ktora zatrzymuje produkcje:
//   0x47369f: call 42C6F0 gate ogolny (bool)
//   0x4736b5: call 42DA65 thiscall(unit, selgood)      - bramka produkcji gooda
//   0x473715: call 44B58A thiscall(unit, selgood)      - czy good niedozwolony?
//   0x47373a: call 42C977 thiscall(unit)               - stan jednostki
//   0x47375c: call 4316F3 thiscall(building, good, 1)   - REVMap bramka budynku
//   0x47377c: call 431DDF thiscall(building, selgood)  - druga bramka
// Stany +0xACC: 0->praca w tle, 2/4->powrot, 5->zajety praca (0x473791)
static const uintptr_t VA_GATE_42DA65 = 0x42DA65;
static const uintptr_t VA_GATE_42DB20 = 0x42DB20;  // czy good na liscie produkcyjnej joba?
static const uintptr_t VA_GATE_44B58A = 0x44B58A;
static const uintptr_t VA_GATE_42C977 = 0x42C977;
static const uintptr_t VA_GATE_4316F3 = 0x4316F3;
static const uintptr_t VA_GATE_431DDF = 0x431DDF;
static const uintptr_t VA_TICK_473618 = 0x473618;  // handler +0xAB8==0x5A (sasiad 473461)

// Faza 1.6 - rozwiazanie kolizji w bramce 431DDF (ret 4 potwierdzone dis16)
static const uintptr_t VA_GATE_431CED = 0x431CED;  // wymagana ilosc; arg = SLOT (nie dobro!)
static const uintptr_t VA_GATE_431F37 = 0x431F37;  // revmap dobro->slot; arg = good (brak boundsu!)

// Faza 3 - lancuch ZAKONCZENIA produkcji (odkryty 2026-10-19 wieczorem):
//   0x45C17B: thiscall(unit, actionId, param) ret 8
//             actionId = rekord receptury +0x4C; bramka: byte[jobRec+0x24+actionId] != 0.
//             Ustawia unit[0xAB8]=actionId, unit[0xABC]=1, unit[0xAC0]=idx akcji.
//   0x468BAE: thiscall(unit) - "zakoncz produkcje": 431B53(bldg, selgood, amount/10, amount%10, 0)
//   0x431B53: thiscall(bldg, good, amount, frac, flag) ret 0x10
//             JEDYNY zapis do magazynu: [bldg+slot*4+0x118] += amount,
//             [bldg+slot*4+0x220] = frac (ulamek /10, clamp 1000).
static const uintptr_t VA_SET_ACTION   = 0x45C17B;
static const uintptr_t VA_PROD_FINISH  = 0x468BAE;
static const uintptr_t VA_STOCK_WRITE  = 0x431B53;

// Globals gry
static const uintptr_t VA_PBUILDINGS   = 0x510BD0;  // [0x510BD0] = wsk. na tablice instancji budynkow
static const size_t    STRIDE_BUILDING = 0x7E0;
static const uintptr_t VA_PHOUSE       = 0x5113A0;  // [0x5113A0] = tablica house_types
static const size_t    STRIDE_HOUSE    = 0x624;      // rekord house_type
static const uintptr_t VA_PPRODLIST    = 0x511200;   // tablica list produkcyjnych jobow
static const size_t    STRIDE_PLIST    = 0x215E0;    // * p (plemie jednostki, unit+0x14) - po relokacji EtapC (NEW_REC_SIZE)
static const size_t    OFF_PLIST_JOB   = 0x6928;     // + job*0x400; count @+4, lista dword @+0xD8
static const uint32_t  OFF_STOCK_CNT   = 0x118;      // stock_count[] w budynku
static const uint32_t  OFF_STOCK_LIST  = 0x60;       // house_type: licznik wpisow logicstock
static const uint32_t  STOCK_ENTRY_SIZE= 0x0C;       // wpis logicstock: {good, qty, flag}
static const uint32_t  OFF_REV_MAP     = 0x37C;      // stock_revmap[] w house_type (good<122 = bezp. w rekordzie)
static const uintptr_t VA_PJOBS        = 0x511180;   // [0x511180] = tablica rekordow jobow
static const size_t    STRIDE_JOB      = 0x88;       // rekord joba
static const uint32_t  OFF_JOB_ALLOW   = 0x24;       // +0x24..+0x87: 100 bajtow = dozwolone actionId

// Offsety w jednostce (z RE - re_summary.md / potwierdzone w disasm)
static const uint32_t U_JOB        = 0x18;    // job ID
static const uint32_t U_SELGOOD    = 0x1C;    // selected good
static const uint32_t U_TIMER      = 0x158;   // production timer
static const uint32_t U_BLDG_IDX   = 0xB34;   // building index (disasm 0x473470)
static const uint32_t U_CANPROD    = 0x195;   // can_produce[good] (bajty)
static const uint32_t B_HOUSETYPE  = 0x14;    // house_type index w instancji budynku

static const uint32_t GOOD_COAL    = 66;      // wegiel
static const uint32_t JOB_SMOLARZ  = 56;
static const uint32_t TYPE_SMOLARNIA = 57;

// ============================================================================
// Log (logs\cnmod_hook.log, z limitem linii - bez spamu)
// ============================================================================

static FILE*      g_log    = nullptr;
static uint32_t   g_lines  = 0;
static const uint32_t MAX_LINES = 120000;

static void clog(const char* fmt, ...)
{
    if (!g_log) return;
    if (g_lines >= MAX_LINES) {
        if (g_lines == MAX_LINES) {
            fputs("[cnmod] LIMIT linii osiagniety - dalsze logi wylaczone\n", g_log);
            fflush(g_log);
        }
        g_lines++;
        return;
    }
    va_list ap;
    va_start(ap, fmt);
    vfprintf(g_log, fmt, ap);
    va_end(ap);
    fflush(g_log);
    g_lines++;
}

// ============================================================================
// Stan diagnostyczny
// ============================================================================

// liczniki ogolne (dump przy detach)
static uint64_t g_nUnitTick = 0, g_nDispatcher = 0, g_nPotter = 0;
static uint64_t g_nCase46BDC1 = 0, g_nFindOwner = 0, g_nFindOwnerNull = 0;
static uint64_t g_nStock66P = 0, g_nStock66N = 0;
static int64_t  g_sum66P = 0, g_sum66N = 0;

// cache jednostek (logowanie tylko na zmianie / co N tickow)
struct UnitCache { void* unit; uint32_t job; uint32_t htype; uint32_t calls; };
static UnitCache g_ucache[512];
static uint32_t  g_ucacheN = 0;

// cache owner-entry (fun 0x43267F)
struct OwnerCache { void* bldg; uint32_t key; void* ret; };
static OwnerCache g_ocache[128];
static uint32_t   g_ocacheN = 0;
static bool       g_b644Dumped = false;

static bool ucache_get(void* u, UnitCache** out)
{
    for (uint32_t i = 0; i < g_ucacheN; i++)
        if (g_ucache[i].unit == u) { *out = &g_ucache[i]; return true; }
    return false;
}

static uint32_t house_type_of(void* unit)
{
    uint32_t idx = *(uint32_t*)((char*)unit + U_BLDG_IDX);
    uintptr_t base = *(uintptr_t*)VA_PBUILDINGS;
    if (!base || idx > 0x4000) return 0xFFFFFFFF;
    return *(uint32_t*)(base + (size_t)idx * STRIDE_BUILDING + B_HOUSETYPE);
}

// Rekord joba (tablica [0x511180], stride 0x88). Zwraca nullptr gdy job poza zakresem.
static char* job_rec(uint32_t job)
{
    uintptr_t base = *(uintptr_t*)VA_PJOBS;
    if (!base || job > 0x200) return nullptr;
    return (char*)base + (size_t)job * STRIDE_JOB;
}

static char* house_rec(uint32_t htype)
{
    uintptr_t base = *(uintptr_t*)VA_PHOUSE;
    if (!base || htype > 0x400) return nullptr;
    return (char*)base + (size_t)htype * STRIDE_HOUSE;
}

// ============================================================================
// Typy oryginalow + wskazniki trampolin (MinHook)
// ============================================================================

typedef void   (__fastcall *FnUnitTick) (void* self, void* edx, int32_t delta);
typedef void   (__fastcall *FnUnit0)    (void* self, void* edx);
typedef void*  (__fastcall *FnFindOwner)(void* self, void* edx, uint32_t key);
typedef void   (__fastcall *FnStockAdd) (void* self, void* edx, int32_t good, int32_t qty);
typedef int32_t (__fastcall *FnGateUG)  (void* self, void* edx, int32_t good);              // 42DA65, 44B58A
typedef int32_t (__fastcall *FnGateU)   (void* self, void* edx);                            // 42C977
typedef int32_t (__fastcall *FnGateBG)  (void* self, void* edx, int32_t good, int32_t flag);// 4316F3
typedef int32_t (__fastcall *FnGateBG1) (void* self, void* edx, int32_t good);              // 431DDF
typedef int32_t (__fastcall *FnGateList)(void* self, void* edx, int32_t good);              // 42DB20
typedef int32_t (__fastcall *FnSetAction)(void* self, void* edx, int32_t actionId, int32_t param); // 45C17B
typedef int32_t (__fastcall *FnStockWrite)(void* self, void* edx, int32_t good, int32_t amount,
                                           int32_t frac, int32_t flag);                     // 431B53

static FnUnitTick  o_unit_tick  = nullptr;
static FnUnit0     o_dispatcher = nullptr;
static FnUnit0     o_potter     = nullptr;
static FnUnit0     o_case46bdc1 = nullptr;
static FnFindOwner o_find_owner = nullptr;
static FnStockAdd  o_stock_add  = nullptr;
static FnGateUG    o_gate_42da65 = nullptr;
static FnGateUG    o_gate_44b58a = nullptr;
static FnGateU     o_gate_42c977 = nullptr;
static FnGateBG    o_gate_4316f3 = nullptr;
static FnGateBG1   o_gate_431ddf = nullptr;
static FnUnitTick  o_tick_473618 = nullptr;
static FnGateBG1   o_gate_431ced = nullptr;   // Faza 1.6
static FnGateBG1   o_gate_431f37 = nullptr;   // Faza 1.6
static FnSetAction o_set_action  = nullptr;   // Faza 3
static FnUnit0     o_prod_finish = nullptr;   // Faza 3
static FnStockWrite o_stock_write = nullptr;  // Faza 3

// ============================================================================
// Detour: FUN_00473461 - unit tick (logowanie na wejsciu)
// ============================================================================

static void __fastcall hook_unit_tick(void* self, void* edx, int32_t delta)
{
    g_nUnitTick++;

    uint32_t job    = *(uint32_t*)((char*)self + U_JOB);
    uint32_t htype  = house_type_of(self);

    UnitCache* c = nullptr;
    bool isNew = !ucache_get(self, &c);
    if (isNew && g_ucacheN < 512) {
        c = &g_ucache[g_ucacheN++];
        c->unit = self; c->job = 0xFFFFFFFF; c->htype = 0xFFFFFFFF; c->calls = 0;
    }
    if (c) {
        c->calls++;
        bool changed = (c->job != job || c->htype != htype);
        bool interesting = (job == JOB_SMOLARZ || htype == TYPE_SMOLARNIA);
        bool heartbeat = interesting && (c->calls % 500 == 0);

        if (isNew && g_nUnitTick <= 300) {
            clog("[tick#1] unit=%p job=%u htype=%u (delta=%d)\n",
                 self, job, htype, delta);
        } else if (changed) {
            clog("[tick] unit=%p job=%u->%u htype=%u->%u\n",
                 self, c->job, job, c->htype, htype);
        } else if (heartbeat) {
            uint32_t timer = *(uint32_t*)((char*)self + U_TIMER);
            uint32_t sel   = *(uint32_t*)((char*)self + U_SELGOOD);
            uint8_t  cp    = *((uint8_t*)self + U_CANPROD + GOOD_COAL);
            clog("[tick#hb] unit=%p job=%u htype=%u timer=%u selgood=%u canprod[66]=%u\n",
                 self, job, htype, timer, sel, cp);
        }
        if (changed || isNew) { c->job = job; c->htype = htype; }
    }

    o_unit_tick(self, edx, delta);
}

// ============================================================================
// Detour: FUN_0046BAD7 - dyspozytor (logowanie na wejsciu)
// ============================================================================

static void __fastcall hook_dispatcher(void* self, void* edx)
{
    g_nDispatcher++;
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);

    if (job == JOB_SMOLARZ) {
        clog("[disp] SMOLARZ unit=%p state+0xACC=%u +0xAB8=%u +0xAD4=%u htype=%u (wywolanie %llu)\n",
             self,
             *(uint32_t*)((char*)self + 0xACC),
             *(uint32_t*)((char*)self + 0xAB8),
             *(uint32_t*)((char*)self + 0xAD4),
             house_type_of(self),
             (unsigned long long)g_nDispatcher);
    } else if (g_nDispatcher % 5000 == 0) {
        clog("[disp#hb] unit=%p job=%u (wywolanie %llu)\n",
             self, job, (unsigned long long)g_nDispatcher);
    }
    o_dispatcher(self, edx);
}

// ============================================================================
// Detour: FUN_0046D53A - potter handler (czy produkcja jest wywolywana?)
// ============================================================================

static void __fastcall hook_potter(void* self, void* edx)
{
    g_nPotter++;
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);
    if (job == JOB_SMOLARZ) {
        clog("[potter] SMOLARZ unit=%p htype=%u (wywolanie %llu)\n",
             self, house_type_of(self), (unsigned long long)g_nPotter);
    } else if (g_nPotter % 5000 == 0) {
        clog("[potter#hb] unit=%p job=%u\n", self, job);
    }
    o_potter(self, edx);
}

// ============================================================================
// Detour: FUN_00473695 - cel przekierowania patcha 614 (>47 -> 0x46BDC1)
// To jest wlasciwy kandydat na "handler produkcji joba 56".
// ============================================================================

static void __fastcall hook_case46bdc1(void* self, void* edx)
{
    g_nCase46BDC1++;
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);
    uint32_t sel = *(uint32_t*)((char*)self + U_SELGOOD);

    if (job == JOB_SMOLARZ) {
        clog("[case46BDC1] SMOLARZ unit=%p htype=%u selgood=%u timer=%u acc=%u (wywolanie %llu)\n",
             self, house_type_of(self), sel,
             *(uint32_t*)((char*)self + U_TIMER),
             *(uint32_t*)((char*)self + 0xACC),
             (unsigned long long)g_nCase46BDC1);
    } else if (g_nCase46BDC1 % 5000 == 0) {
        clog("[case46BDC1#hb] unit=%p job=%u\n", self, job);
    }
    o_case46bdc1(self, edx);
    if (job == JOB_SMOLARZ) {
        clog("[case46BDC1] SMOLARZ PO: unit=%p acc=%u +0x36c=%u +0x374=%u +0xAD0=%u\n",
             self,
             *(uint32_t*)((char*)self + 0xACC),
             *(uint32_t*)((char*)self + 0x36C),
             *(uint32_t*)((char*)self + 0x374),
             *(uint32_t*)((char*)self + 0xAD0));
    }
}

// ============================================================================
// Detour: FUN_0043267F - find owner entry (case38); zwraca NULL → AV na 0x4734C6
// ============================================================================

static void* __fastcall hook_find_owner(void* self, void* edx, uint32_t key)
{
    g_nFindOwner++;
    void* ret = o_find_owner(self, edx, key);

    uint32_t htype = *(uint32_t*)((char*)self + B_HOUSETYPE);

    // Diagnostyka: jednorazowy zrzut tablicy wlascicieli dla smolarni.
    // Pokazuje, jakie wpisy (owner/tribe) budynek faktycznie ma w +0x644.
    if (!g_b644Dumped && htype == TYPE_SMOLARNIA) {
        g_b644Dumped = true;
        clog("[owner] DUMP +0x644 htype=57 key=0x%X ret=%p\n", key, ret);
        for (uint32_t i = 0; i < 20; i++) {
            uint32_t v = *(uint32_t*)((char*)self + 0x644 + i * 4);
            if (v)
                clog("   +0x%03X [%02u] = %u (0x%X)\n", 0x644 + i * 4, i, v, v);
        }
    }

    bool interesting = (htype == TYPE_SMOLARNIA || ret == nullptr);

    // cache: loguj tylko na zmianie (albo zawsze dla NULL - bezpiecznictwo)
    bool changed = false;
    if (interesting) {
        bool found = false;
        for (uint32_t i = 0; i < g_ocacheN; i++) {
            if (g_ocache[i].bldg == self) {
                if (g_ocache[i].key != key || g_ocache[i].ret != ret) changed = true;
                g_ocache[i].key = key; g_ocache[i].ret = ret;
                found = true; break;
            }
        }
        if (!found && g_ocacheN < 128) {
            g_ocache[g_ocacheN].bldg = self;
            g_ocache[g_ocacheN].key  = key;
            g_ocache[g_ocacheN].ret  = ret;
            g_ocacheN++;
            changed = true;
        }
    }

    if (ret == nullptr) {
        g_nFindOwnerNull++;
        // Inne miejsca wywolujace te funkcje tez dostaja NULL (gra to obsluguje)
        // - logujemy tylko htype 57 i pierwszych 20, zeby nie zalac logu.
        if (htype == TYPE_SMOLARNIA || g_nFindOwnerNull <= 20) {
            clog("[owner] NULL! building=%p key=0x%X htype=%u (licznik=%llu)\n",
                 self, key, htype, (unsigned long long)g_nFindOwnerNull);
        }
    } else if (htype == TYPE_SMOLARNIA && changed) {
        uint32_t f8  = *(uint32_t*)((char*)ret + 8);
        uint32_t f12 = *(uint32_t*)((char*)ret + 0xC);
        clog("[owner] SMOLARNIA building=%p key=0x%X ret=%p "
             "[ret+8]=%u (=prawd. 'good') [ret+0xC]=%u (htype=%u)\n",
             self, key, ret, f8, f12, htype);
    }
    return ret;
}

// ============================================================================
// Detour: FUN_0044B910 - dodanie/odejmienie towaru w stocku
// Tu WIDAC produkcje: good 66 z qty>0 = powstal wegiel!
// ============================================================================

static void __fastcall hook_stock_add(void* self, void* edx, int32_t good, int32_t qty)
{
    if (good == (int32_t)GOOD_COAL) {
        if (qty >= 0) { g_nStock66P++; g_sum66P += qty; }
        else          { g_nStock66N++; g_sum66N += qty; }
        clog("[stock] WEGL good=66 qty=%+d stockobj=%p (prod #%llu / zuzyc #%llu, bilans=%lld)\n",
             qty, self,
             (unsigned long long)g_nStock66P,
             (unsigned long long)g_nStock66N,
             (long long)(g_sum66P + g_sum66N));
    }
    o_stock_add(self, edx, good, qty);
}

// ============================================================================
// Detoury bramek sciezki produkcji (ktora zatrzymuje smolarnie?)
// Logujemy tylko good==66 (wegiel) lub budynki htype 57 - bez spamu.
// ============================================================================

static uint64_t g_nG42DA65 = 0, g_nG44B58A = 0, g_nG42C977 = 0, g_nG4316F3 = 0, g_nG431DDF = 0;
static uint64_t g_nTick473618 = 0;

static int32_t __fastcall hook_gate_42da65(void* self, void* edx, int32_t good)
{
    int32_t r = o_gate_42da65(self, edx, good);
    g_nG42DA65++;
    if (good == (int32_t)GOOD_COAL) {
        // Faza 1.6 (U1): listCount z [0x511200]+p*0x1AE08+0x6928+job*0x400+4
        uint32_t ujob = *(uint32_t*)((char*)self + U_JOB);
        uint32_t p    = *(uint32_t*)((char*)self + 0x14);
        uintptr_t tb  = *(uintptr_t*)VA_PPRODLIST;
        uint32_t cnt = 0xFFFFFFFF, l0 = 0, l1 = 0, l2 = 0;
        if (tb && p < 0x100 && ujob < 512) {
            uintptr_t sl = tb + (uintptr_t)p * STRIDE_PLIST + OFF_PLIST_JOB + (uintptr_t)ujob * 0x400;
            cnt = *(uint32_t*)(sl + 4);
            l0  = *(uint32_t*)(sl + 0xD8);
            l1  = *(uint32_t*)(sl + 0xDC);
            l2  = *(uint32_t*)(sl + 0xE0);
        }
        uint8_t cp = *((uint8_t*)self + U_CANPROD + GOOD_COAL);
        clog("[gate 42DA65] unit=%p job=%u good=%d -> %d listCount=%u list=[%u,%u,%u] canprod66=%u (#%llu)\n",
             self, ujob, good, r, cnt, l0, l1, l2, cp,
             (unsigned long long)g_nG42DA65);
    }
    return r;
}

static int32_t __fastcall hook_gate_44b58a(void* self, void* edx, int32_t good)
{
    int32_t r = o_gate_44b58a(self, edx, good);
    g_nG44B58A++;
    if (good == (int32_t)GOOD_COAL) {
        clog("[gate 44B58A] unit=%p good=%d -> %d (wywolanie %llu)\n",
             self, good, r, (unsigned long long)g_nG44B58A);
    }
    return r;
}

static int32_t __fastcall hook_gate_42c977(void* self, void* edx)
{
    int32_t r = o_gate_42c977(self, edx);
    g_nG42C977++;
    if (r == 0 && g_nG42C977 % 3000 == 0) {
        clog("[gate 42C977] unit=%p job=%u -> 0 (hibernacja? wywolanie %llu)\n",
             self, *(uint32_t*)((char*)self + U_JOB), (unsigned long long)g_nG42C977);
    }
    return r;
}

static int32_t __fastcall hook_gate_4316f3(void* self, void* edx, int32_t good, int32_t flag)
{
    int32_t r = o_gate_4316f3(self, edx, good, flag);
    g_nG4316F3++;
    if (good == (int32_t)GOOD_COAL) {
        clog("[gate 4316F3 REVMap] building=%p htype=%u good=%d flag=%d -> %d (wywolanie %llu)\n",
             self, *(uint32_t*)((char*)self + B_HOUSETYPE), good, flag, r,
             (unsigned long long)g_nG4316F3);
    }
    return r;
}

// --- Faza 1.6: rozwiazanie kolizji przy good 66 ------------------------------
// 431DDF loguje: smolarnie (htype 57, KAŻDE dobro), good 66 z dowolnego
// budynku (dostawa do magazynu = U3) + probke piekarni/mlyna (htype 13/14)
// jako wzorzec dzialania vanilla.
// slotR = surowy odczyt revmap[good] (+0x37C+good*4; do good=121 w granicach
// rekordu). Dla towarow specjalnych 18-22 gdy surowy == -1 oryginal 431F37
// zwraca +0x3BC/+0x3C0 - prawdziwy slot widac wtedy w logu [g431CED].
static uint64_t g_nG431CED = 0, g_nG431F37 = 0;
static uint32_t g_smpCED1314 = 0, g_smpCED79 = 0, g_smpDDF1314 = 0;

static int32_t __fastcall hook_gate_431ddf(void* self, void* edx, int32_t good)
{
    int32_t r = o_gate_431ddf(self, edx, good);
    g_nG431DDF++;
    uint32_t htype = *(uint32_t*)((char*)self + B_HOUSETYPE);
    bool log = (htype == TYPE_SMOLARNIA || good == (int32_t)GOOD_COAL);
    if (!log && (htype == 13 || htype == 14) && g_smpDDF1314 < 300) {
        log = true; g_smpDDF1314++;
    }
    if (log) {
        uint32_t slotR = 0xFFFFFFFF;
        int32_t  stock = -1;
        char* rec = house_rec(htype);
        if (rec && good >= 0 && good < 122) {
            slotR = *(uint32_t*)(rec + OFF_REV_MAP + (size_t)good * 4);
            if (slotR < 122)
                stock = (int32_t)*(uint32_t*)((char*)self + OFF_STOCK_CNT + (size_t)slotR * 4);
        }
        clog("[g431DDF] bldg=%p htype=%u good=%d slotR=%d stock=%d -> %d (#%llu)\n",
             self, htype, good, (int32_t)slotR, stock, r,
             (unsigned long long)g_nG431DDF);
    }
    return r;
}

// FUN_00431CED - wymagana ilosc = house_types[htype].field_0x68[slot].dword0 * mult
// (mult z [0x510BC4]+0x5d200: 1->2, 2->5, inaczej 1). Log: surowe pola + wynik.
static int32_t __fastcall hook_gate_431ced(void* self, void* edx, int32_t slot)
{
    int32_t r = o_gate_431ced(self, edx, slot);
    g_nG431CED++;
    uint32_t htype = *(uint32_t*)((char*)self + B_HOUSETYPE);
    bool log = (htype == TYPE_SMOLARNIA);
    if (!log && (htype == 13 || htype == 14) && g_smpCED1314 < 150) { log = true; g_smpCED1314++; }
    if (!log && htype >= 7 && htype <= 9 && g_smpCED79 < 50)        { log = true; g_smpCED79++; }
    if (log) {
        uint32_t raw0 = 0, raw1 = 0;
        char* rec = house_rec(htype);
        if (rec && slot >= 0 && slot < 122) {
            raw0 = *(uint32_t*)(rec + 0x68 + (size_t)slot * 12);
            raw1 = *(uint32_t*)(rec + 0x68 + (size_t)slot * 12 + 4);
        }
        clog("[g431CED] bldg=%p htype=%u slot=%d field0=%u field1=%d -> req=%d (#%llu)\n",
             self, htype, slot, raw0, (int32_t)raw1, r,
             (unsigned long long)g_nG431CED);
    }
    return r;
}

// FUN_00431F37 - revmap[good] (oryginal bez boundsu - good 66 czyta +0x484!)
//
// BUG (znaleziony 22.10.2026): tablica revmap w rekordzie house_type ma tylko
// 66 wpisow (dobra 0..65). Dla dobra 66 odczyt trafia w pole +0x484, czyli
// LICZNIK listy "logicproduction". Skutek: KAZDE dobro >= 66 mapuje sie na
// slot rowny liczbie produktow (zwykle 1) w KAZDYM budynku - np. wegiel
// trafial do piekarni do slotu 1, ktory jest slotem MAKI ("wegiel zamienia
// sie w make").
//
// Strażnik: dziala tylko dla dobr >= 66. Sprawdza, czy zwrocony slot
// faktycznie przechowuje to dobro wg tablicy logicstock tego htype
// (count @ +0x60, wpisy {good, qty, flag} po 12 bajtow od +0x64).
// Jesli nie - zwraca -1 (budynek nie przyjmuje tego dobra).
//   chata smolarza (ht 57): slot1 -> good 66  -> przepuszcza (poprawnie)
//   piekarnia      (ht 13): slot1 -> good 11  -> blokuje
static int32_t __fastcall hook_gate_431f37(void* self, void* edx, int32_t good)
{
    int32_t r = o_gate_431f37(self, edx, good);
    g_nG431F37++;

    if (good >= (int32_t)GOOD_COAL && r >= 0) {
        uint32_t htype = *(uint32_t*)((char*)self + B_HOUSETYPE);
        char* rec = house_rec(htype);
        if (rec) {
            uint32_t cnt = *(uint32_t*)(rec + OFF_STOCK_LIST);
            int32_t  slotgood = -1;
            if ((uint32_t)r < cnt)
                slotgood = *(int32_t*)(rec + OFF_STOCK_LIST + 4 + (size_t)r * STOCK_ENTRY_SIZE);
            if (slotgood != good) {
                if (g_nG431F37 < 40 || (g_nG431F37 % 3000) == 0) {
                    clog("[g431F37 BLOCK] bldg=%p htype=%u good=%d -> slot %d (tam dobro %d) => -1 (#%llu)\n",
                         self, htype, good, r, slotgood, (unsigned long long)g_nG431F37);
                }
                return -1;
            }
        }
    }

    if (good == (int32_t)GOOD_COAL) {
        clog("[g431F37] bldg=%p htype=%u good=%d -> slot=%d (#%llu)\n",
             self, *(uint32_t*)((char*)self + B_HOUSETYPE), good, r,
             (unsigned long long)g_nG431F37);
    }
    return r;
}

// Alternatywny tick +0xAB8==0x5A (sasiad 473461) - czy smolarz w ogole tu wchodzi?
static void __fastcall hook_tick_473618(void* self, void* edx, int32_t delta)
{
    g_nTick473618++;
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);
    if (job == JOB_SMOLARZ) {
        clog("[tick473618] SMOLARZ unit=%p htype=%u delta=%d (wywolanie %llu)\n",
             self, house_type_of(self), delta, (unsigned long long)g_nTick473618);
    }
    o_tick_473618(self, edx, delta);
}

// ============================================================================
// Faza 3 - hooki lancucha zakonczenia produkcji
// ============================================================================

static uint64_t g_nSetAction = 0, g_nProdFinish = 0, g_nStockWrite = 0;

// 45C17B(unit, actionId, param): actionId = rec[+0x4C]; zwraca 0 gdy whitelista
// joba (byte[jobRec+0x24+actionId]) == 0. Dla smolarza actionId = 38.
static int32_t __fastcall hook_set_action(void* self, void* edx, int32_t actionId, int32_t param)
{
    g_nSetAction++;
    int32_t r = o_set_action(self, edx, actionId, param);
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);
    if (job == JOB_SMOLARZ) {
        uint32_t jobRecOff = 0x24 + (uint32_t)actionId;
        uint32_t allow = 0xFF;   // 0xFF = actionId poza rekordem joba
        char* jr = job_rec(job);
        if (jr && actionId >= 0 && actionId < 100) allow = *(uint8_t*)(jr + jobRecOff);
        clog("[setAction] SMOLARZ unit=%p actionId=%d allow=%u param=%d -> %d"
             " | ab8=%u abc=%u ac0=%u ac8=%u ad0=%u\n",
             self, actionId, allow, param, r,
             *(uint32_t*)((char*)self + 0xAB8),
             (uint32_t)*(uint8_t*)((char*)self + 0xABC),
             *(uint32_t*)((char*)self + 0xAC0),
             *(uint32_t*)((char*)self + 0xAC8),
             *(uint32_t*)((char*)self + 0xAD0));
    }
    return r;
}

// 468BAE(unit): zakonczenie produkcji - dodaje wyjscie do magazynu.
static void __fastcall hook_prod_finish(void* self, void* edx)
{
    g_nProdFinish++;
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);
    if (job == JOB_SMOLARZ) {
        clog("[prodFinish] SMOLARZ unit=%p selgood=%u 36c=%u acc=%u ad0=%u\n",
             self, *(uint32_t*)((char*)self + U_SELGOOD),
             *(uint32_t*)((char*)self + 0x36C),
             *(uint32_t*)((char*)self + 0xACC),
             *(uint32_t*)((char*)self + 0xAD0));
    }
    o_prod_finish(self, edx);
}

// 431B53(bldg, good, amount, frac, flag): jedyny zapis do magazynu budynku.
static int32_t __fastcall hook_stock_write(void* self, void* edx, int32_t good, int32_t amount,
                                           int32_t frac, int32_t flag)
{
    g_nStockWrite++;
    int32_t r = o_stock_write(self, edx, good, amount, frac, flag);
    uint32_t htype = *(uint32_t*)((char*)self + B_HOUSETYPE);
    if (htype == TYPE_SMOLARNIA || good == (int32_t)GOOD_COAL) {
        clog("[stockWrite] bldg=%p htype=%u good=%d amount=%d frac=%d flag=%d -> %d\n",
             self, htype, good, amount, frac, flag, r);
    }
    return r;
}

// ============================================================================
// Instalacja hookow
// ============================================================================

static bool g_installed = false;

static bool install_one(const char* name, uintptr_t addr, LPVOID detour, LPVOID* orig)
{
    MH_STATUS st = MH_CreateHook((LPVOID)addr, detour, orig);
    if (st != MH_OK) {
        clog("[init] BLAD %s: MH_CreateHook(0x%X) = %d\n", name, (unsigned)addr, (int)st);
        return false;
    }
    clog("[init] hook %s @0x%X OK\n", name, (unsigned)addr);
    return true;
}

static bool install_hooks()
{
    MH_STATUS st = MH_Initialize();
    if (st != MH_OK && st != MH_ERROR_ALREADY_INITIALIZED) {
        clog("[init] MH_Initialize = %d\n", (int)st);
        return false;
    }
    bool ok = true;
    ok &= install_one("unit_tick(473461)",  VA_UNIT_TICK,  (LPVOID)&hook_unit_tick,  (LPVOID*)&o_unit_tick);
    ok &= install_one("dispatcher(46BAD7)", VA_DISPATCHER, (LPVOID)&hook_dispatcher, (LPVOID*)&o_dispatcher);
    ok &= install_one("potter(46D53A)",     VA_POTTER,     (LPVOID)&hook_potter,     (LPVOID*)&o_potter);
    ok &= install_one("case46BDC1(473695)", VA_CASE46BDC1, (LPVOID)&hook_case46bdc1, (LPVOID*)&o_case46bdc1);
    ok &= install_one("find_owner(43267F)", VA_FIND_OWNER, (LPVOID)&hook_find_owner, (LPVOID*)&o_find_owner);
    ok &= install_one("stock_add(44B910)",  VA_STOCK_ADD,  (LPVOID)&hook_stock_add,  (LPVOID*)&o_stock_add);
    ok &= install_one("gate 42DA65",        VA_GATE_42DA65,(LPVOID)&hook_gate_42da65,(LPVOID*)&o_gate_42da65);
    ok &= install_one("gate 44B58A",        VA_GATE_44B58A,(LPVOID)&hook_gate_44b58a,(LPVOID*)&o_gate_44b58a);
    ok &= install_one("gate 42C977",        VA_GATE_42C977,(LPVOID)&hook_gate_42c977,(LPVOID*)&o_gate_42c977);
    ok &= install_one("gate 4316F3",        VA_GATE_4316F3,(LPVOID)&hook_gate_4316f3,(LPVOID*)&o_gate_4316f3);
    ok &= install_one("gate 431DDF",        VA_GATE_431DDF,(LPVOID)&hook_gate_431ddf,(LPVOID*)&o_gate_431ddf);
    ok &= install_one("gate 431CED",        VA_GATE_431CED,(LPVOID)&hook_gate_431ced,(LPVOID*)&o_gate_431ced);
    ok &= install_one("gate 431F37",        VA_GATE_431F37,(LPVOID)&hook_gate_431f37,(LPVOID*)&o_gate_431f37);
    ok &= install_one("tick 473618",        VA_TICK_473618,(LPVOID)&hook_tick_473618,(LPVOID*)&o_tick_473618);
    ok &= install_one("set_action(45C17B)",  VA_SET_ACTION,  (LPVOID)&hook_set_action,  (LPVOID*)&o_set_action);
    ok &= install_one("prod_finish(468BAE)", VA_PROD_FINISH, (LPVOID)&hook_prod_finish, (LPVOID*)&o_prod_finish);
    ok &= install_one("stock_write(431B53)", VA_STOCK_WRITE, (LPVOID)&hook_stock_write, (LPVOID*)&o_stock_write);

    if (ok) {
        st = MH_EnableHook(MH_ALL_HOOKS);
        if (st != MH_OK) {
            clog("[init] MH_EnableHook = %d\n", (int)st);
            return false;
        }
        clog("[init] wszystkie hooki zainstalowane i wlaczone\n");
    }
    return ok;
}

static void shutdown_hooks()
{
    if (!g_installed) return;
    MH_DisableHook(MH_ALL_HOOKS);
    MH_Uninitialize();
    clog("[exit] === PODSUMOWANIE ===\n"
         "[exit] unit_tick=%llu dispatcher=%llu potter=%llu case46BDC1=%llu\n"
         "[exit] find_owner=%llu (NULL=%llu) stock66: prod#=%llu sum=%lld | zuż#=%llu sum=%lld\n"
         "[exit] bramki: 42DA65=%llu 44B58A=%llu 42C977=%llu 4316F3=%llu 431DDF=%llu tick473618=%llu\n"
         "[exit] Faza1.6: 431CED=%llu 431F37=%llu probki ced(13/14)=%u ced(7-9)=%u ddf(13/14)=%u\n"
         "[exit] Faza3: set_action=%llu prod_finish=%llu stock_write=%llu\n"
         "[exit] linii logu=%u\n",
         (unsigned long long)g_nUnitTick, (unsigned long long)g_nDispatcher,
         (unsigned long long)g_nPotter,   (unsigned long long)g_nCase46BDC1,
         (unsigned long long)g_nFindOwner, (unsigned long long)g_nFindOwnerNull,
         (unsigned long long)g_nStock66P, (long long)g_sum66P,
         (unsigned long long)g_nStock66N, (long long)g_sum66N,
         (unsigned long long)g_nG42DA65, (unsigned long long)g_nG44B58A,
         (unsigned long long)g_nG42C977, (unsigned long long)g_nG4316F3,
         (unsigned long long)g_nG431DDF, (unsigned long long)g_nTick473618,
         (unsigned long long)g_nG431CED, (unsigned long long)g_nG431F37,
         g_smpCED1314, g_smpCED79, g_smpDDF1314,
         (unsigned long long)g_nSetAction, (unsigned long long)g_nProdFinish,
         (unsigned long long)g_nStockWrite,
         g_lines);
}

// ============================================================================
// Eksporty (zgodne z include/cnmod_hook.h)
// ============================================================================

extern "C" bool CNMod_Initialize()
{
    if (g_installed) return true;
    g_installed = install_hooks();
    return g_installed;
}

extern "C" void CNMod_Shutdown()
{
    shutdown_hooks();
    g_installed = false;
}

extern "C" bool CNMod_RegisterJob(uint32_t jobId, void* handler, void* context)
{
    (void)jobId; (void)handler; (void)context;
    return false;  // Faza 3 (rejestracja custom jobow)
}

extern "C" void CNMod_UnregisterJob(uint32_t jobId) { (void)jobId; }
extern "C" uint32_t CNMod_GetCustomJobCount() { return 0; }
extern "C" bool CNMod_IsInitialized() { return g_installed; }

// ============================================================================
// DllMain
// ============================================================================

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved)
{
    (void)lpReserved;
    switch (reason) {
    case DLL_PROCESS_ATTACH: {
        DisableThreadLibraryCalls(hModule);
        char path[MAX_PATH];
        GetCurrentDirectoryA(MAX_PATH, path);
        strncat(path, "\\logs\\cnmod_hook.log", MAX_PATH - strlen(path) - 1);
        g_log = fopen(path, "a");
        if (g_log) {
            clog("\n[cnmod] ===== cnmod_hook.dll Faza 1.6 (diagnostyka+) =====\n");
            clog("[cnmod] process base=0x%X\n", (unsigned)(uintptr_t)GetModuleHandleA(nullptr));
        }
        g_installed = install_hooks();
        break;
    }
    case DLL_PROCESS_DETACH:
        shutdown_hooks();
        if (g_log) { fclose(g_log); g_log = nullptr; }
        break;
    }
    return TRUE;
}
