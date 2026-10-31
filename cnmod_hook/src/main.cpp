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
#include <string>
#include <unordered_map>
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
static const uintptr_t VA_DRAW_GOOD_ICON = 0x0047E381; // FUN_0047e381: rysowanie ikony dobra
static const uintptr_t VA_INIT_LANDSCAPE_TABLE = 0x412b62; // FUN_00412b62: inicjalizuje tabelę 0x510c60 (landscapetype -> good ID)

// Bramki na sciezce FUN_00473695 (rozklad 2026-10-19) - ktora zatrzymuje produkcje:
//   0x47369f: call 42C6F0 gate ogolny (bool)
//   0x4736b5: call 42DA65 thiscall(unit, selgood)      - bramka produkcji gooda
//   0x473715: call 44B58A thiscall(unit, selgood)      - czy good niedozwolony?
//   0x47373a: call 42C977 thiscall(unit)               - stan jednostki
//   0x47375c: call 4316F3 thiscall(building, good, 1)   - REVMap bramka budynku
//   0x47377c: call 431DDF thiscall(building, selgood)  - druga bramka
// Stany +0xACC: 0->praca w tle, 2/4->powrot, 5->zajety praca (0x473791)
static const uintptr_t VA_GATE_42DA65 = 0x42DA65;
static const uintptr_t VA_SCHED_44A0D9 = 0x44A0D9;
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
static const uintptr_t VA_CATEGORIZE   = 0x45CBBE;   // kategoryzacja dobra (FUN_0045CBBE)
static const uintptr_t VA_CATBUILD     = 0x4A82BB;   // budowa listy goods dla kategorii (FUN_004a82bb)
static const uintptr_t VA_0x419587_QTY = 0x419587;   // FUN_00419587: good active? (rec[+4]!=0 || rec[+0xc]!=0)
static const uintptr_t VA_CARRY_RENDER_42D575 = 0x42D575;
static const uintptr_t VA_PICKUP_4760BF = 0x4760BF;   // inicjacja niesienia dobra
static const uintptr_t VA_CARRY_FRAMES_42CEA6 = 0x42CEA6; // para klatek animacji niesienia (thiscall, 0 arg.)
static const uintptr_t VA_ANIM_LOOKUP_45D14F = 0x45D14F; // szuka wariantu animacji (thiscall, ret 8)
static const uintptr_t VA_ANIM_SETUP_45C23E  = 0x45C23E; // setup sprite'a niesienia (thiscall, ret 8)
static const uintptr_t VA_GATE_46B696 = 0x46B696;     // brama do carry render (if [unit+0xAD4]==0 call 0x42D575)
static const uintptr_t VA_CARRY_LOOKUP_45C94B = 0x45C94B; // lookup carry animation slot
static const uintptr_t VA_ACTION_LOOP_46B621 = 0x46B621;   // main action loop (FUN_0046b621)
// UWAGA (2026-10-30): NIE hookowac 0x4E15B3 ani 0x4E162E.
//   0x4E15B3 (FUN_004e15b3) to lookup TABLICY STRINGOW (zwraca char*, przy braku
//   wpisu zwraca "<%d:%d:NOT DEFINED>"), a 0x4E162E (FUN_004e162e) to
//   FUN_004e15b3(4, x). Wczesniejsze detoury (29.10) mialy zla sygnature,
//   zwracaly smieci i psuly rysowanie.
//   Ikone węgla rysuje parser tagu {gfxgood:%d,1} (FUN_004e1e3f) na podstawie
//   good_types[g]+0x24; pole wypelnia FUN_00415e8a. Patch danych 0x0015EB2
//   (patches_ext.h) rozszerza jego petle na wszystkie rekordy. Bez hooka.

// Diagnostyka wczytywania zapisu (2026-10-28) - TYLKO LOG (osobny plik cnmod_diag.log)
static const uintptr_t VA_WORLD_INIT      = 0x40704B; // cdecl(short,short,char,void*,uchar) - tworzy wszystkie singletony
static const uintptr_t VA_WORLD_CLEANUP   = 0x407291; // cdecl() - niszczy wszystkie singletony
static const uintptr_t VA_GSMX_NEW        = 0x4190AE; // thiscall() -> twórca singletona gsmx (0x740 B)
static const uintptr_t VA_GSMX_LOAD       = 0x41912C; // thiscall(reader) ret 4 -> load-constructor gsmx
static const uintptr_t VA_SAVE_LOADER     = 0x425EC5; // cdecl(reader, uchar) - loader zapisu (petla chunkow)
static const uintptr_t VA_CHUNK_READ      = 0x42A28D; // thiscall(reader) -> naglowek "hoix"+class id
static const uintptr_t VA_DRAW_BUILDING   = 0x4B74C8; // thiscall(a,b) ret 8 - rysowanie budynku (uzywa gsmx)
static const uintptr_t VA_DAT_WORLD_FLAG  = 0x5109F0; // byte: 1 = swiat zainicjowany
static const uintptr_t VA_DAT_GSMX        = 0x5116D4; // ptr: singleton gsmx

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
static const uint32_t MAX_LINES = 500000;

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
static bool       g_good66Dumped = false;
static bool       g_tablePatched = false;
static int        g_carryLookupCalls = 0;
static int        g_actionLoopCalls = 0;

// --- Mapowanie landscapetype -> good ID (ini-configurable) --------------------

static std::unordered_map<uint32_t,uint32_t> g_landscapeGoodMap;
static bool g_landscapeMapLoaded = false;

static void LoadLandscapeGoodMapIni()
{
    const char* path = "CN.PLMOD\\types\\landscape_good_map.ini";
    FILE* f = fopen(path, "r");
    if (!f) { clog("[lgm] Nie mozna wczytac %s\n", path); return; }
    char line[256];
    bool inSec = false;
    while (fgets(line, sizeof(line), f)) {
        char* p = line;
        while (*p==' '||*p=='\t') p++;
        if (*p=='[') {
            if (strncmp(p, "[landscape_good_map]", 20)==0) inSec=true; else inSec=false;
            continue;
        }
        if (!inSec) continue;
        if (*p=='\0'||*p==';'||*p=='#'||*p=='\n'||*p=='\r') continue;
        char* eq = strchr(p, '=');
        if (!eq) continue;
        *eq = '\0';
        uint32_t lt = (uint32_t)atoi(p);
        uint32_t good = (uint32_t)atoi(eq+1);
        g_landscapeGoodMap[lt] = good;
        clog("[lgm] INI: landscapetype=%u -> good=%u\n", lt, good);
    }
    fclose(f);
    g_landscapeMapLoaded = true;
    clog("[lgm] Wczytano %u wpisow z %s\n", (uint32_t)g_landscapeGoodMap.size(), path);
}

// --- Kategoria dobra (ini-configurable) ---------------------------------------

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
typedef int (__cdecl *FnCategorize)(int good);
typedef void (__fastcall *FnCatBuild)(void* self, void* edx);
typedef uint32_t (__fastcall *Fn0x419587)(void* self, void* edx, int good);
typedef void* (__fastcall *FnDrawGoodIcon)(void* self, int good, ...);
typedef void   (__fastcall *FnInitLandscapeTable)(void* self, void* edx);  // 0x412b62: inicjalizuje tabelę 0x510c60

static FnUnitTick  o_unit_tick  = nullptr;
static FnInitLandscapeTable o_init_landscape_table = nullptr;
static FnUnit0     o_dispatcher = nullptr;
static FnUnit0     o_potter     = nullptr;
static FnUnit0     o_case46bdc1 = nullptr;
static FnFindOwner o_find_owner = nullptr;
static FnStockAdd  o_stock_add  = nullptr;
static FnGateUG    o_gate_42da65 = nullptr;
static FnUnit0     o_sched_44a0d9 = nullptr;
static FnGateUG    o_gate_44b58a = nullptr;
static FnGateU     o_gate_42c977 = nullptr;
static FnGateBG    o_gate_4316f3 = nullptr;
static FnGateBG1   o_gate_431ddf = nullptr;
static FnUnitTick  o_tick_473618 = nullptr;
static FnGateBG1   o_gate_431ced = nullptr;   // Faza 1.6
static FnGateBG1   o_gate_431f37 = nullptr;   // Faza 1.6
static FnSetAction o_set_action  = nullptr;   // Faza 3
typedef void (__thiscall *FnCarryRender)(void* self, int param);
static FnCarryRender o_carry_render_42d575 = nullptr;
// FUN_004760BF: thiscall, ZERO argumentow stosu (konczy sie `ret`) - patrz objdump.
typedef void (__thiscall *FnPickup)(void* self);
static FnPickup    o_pickup_4760bf = nullptr;
// FUN_0042CEA6: thiscall, ZERO argumentow stosu, zwraca wskaznik na pare klatek
// animacji niesienia (dla jednostki poza budynkiem: jobs[unit+0xC]+0x12).
typedef int* (__thiscall *FnCarryFrames)(void* self);
static FnCarryFrames o_carry_frames_42cea6 = nullptr;
// FUN_0045D14F / FUN_0045C23E: thiscall, 2 arg. stosu, `ret 8` (sprzata wywolywany).
typedef bool (__thiscall *FnAnimPair)(void* self, short* a, short* b);
static FnAnimPair o_anim_lookup_45d14f = nullptr;
static FnAnimPair o_anim_setup_45c23e  = nullptr;
static void(__thiscall* o_action_loop_46b621)(void*, int) = nullptr;

// zdefiniowana nizej - zrzut tabeli renderu niesionego dobra
static void dump_carry_table_once();

// ============================================================================
// Detour: FUN_00473461 - unit tick (logowanie na wejsciu)
// ============================================================================
static FnUnit0     o_prod_finish = nullptr;   // Faza 3
static FnStockWrite o_stock_write = nullptr;  // Faza 3
static FnCategorize o_categorize = nullptr;   // kategoryzacja dobra
static FnCatBuild   o_catbuild   = nullptr;   // budowa listy goods dla kategorii
static Fn0x419587   o_0x419587_qty = nullptr; // FUN_00419587 oryginalny

// Hook na FUN_0047e381 - rysowanie ikony dobra na mapie / niesionego (case 0xA).
// good 66 (wegiel) nie ma wpisu w tabeli goodgraphics (DAT_00568740, wczytywana
// z goodgraphics.cif) - FUN_0047e381 czytalby -1 i mogl crashowac. Dlatego
// przekierowujemy na good 3 (kamien), ktory ma poprawny wpis.
static FnDrawGoodIcon o_draw_good_icon = nullptr;

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
    // Dobra >= 66 (węgiel i nowe surowce) leżą poza revmap[] (66 wpisów, 0..65).
    // Skanujemy logicstock budynku uniwersalnie, zamiast czytać poza tablicą.
    if (good >= (int32_t)GOOD_COAL) {
        g_nG431F37++;
        uint32_t htype = *(uint32_t*)((char*)self + B_HOUSETYPE);
        char* rec = house_rec(htype);
        if (rec) {
            uint32_t cnt = *(uint32_t*)(rec + OFF_STOCK_LIST);
            for (uint32_t i = 0; i < cnt; i++) {
                if (*(int32_t*)(rec + OFF_STOCK_LIST + 4 + (size_t)i * STOCK_ENTRY_SIZE) == good) {
                    clog("[g431F37] universal: bldg=%p htype=%u good=%d -> slot=%u\n", self, htype, good, i);
                    return (int32_t)i;
                }
            }
        }
        clog("[g431F37] universal: bldg=%p htype=%u good=%d -> NOT FOUND\n", self, htype, good);
        return -1;
    }

    // Dobra >= 66 (węgiel i nowe surowce) leżą poza revmap[] (66 wpisów, 0..65).
    // Skanujemy logicstock budynku uniwersalnie, zamiast czytać poza tablicą.
    if (good >= (int32_t)GOOD_COAL) {
        g_nG431F37++;
        uint32_t htype = *(uint32_t*)((char*)self + B_HOUSETYPE);
        char* rec = house_rec(htype);
        if (rec) {
            uint32_t cnt = *(uint32_t*)(rec + OFF_STOCK_LIST);
            for (uint32_t i = 0; i < cnt; i++) {
                if (*(int32_t*)(rec + OFF_STOCK_LIST + 4 + (size_t)i * STOCK_ENTRY_SIZE) == good) {
                    clog("[g431F37] universal: bldg=%p htype=%u good=%d -> slot=%u\n", self, htype, good, i);
                    return (int32_t)i;
                }
            }
        }
        clog("[g431F37] universal: bldg=%p htype=%u good=%d -> NOT FOUND\n", self, htype, good);
        return -1;
    }

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

    if (!g_good66Dumped) {
        g_good66Dumped = true;
        char** ggt = (char**)0x511420;
        void** gga = (void**)0x568740;
        uint32_t lt = 0xFFFFFFFF, fl = 0xFFFFFFFF;
        if (ggt && *ggt) {
            lt = *(uint32_t*)(*ggt + 66 * 0xD0 + 0x20);
            fl = *(uint32_t*)(*ggt + 66 * 0xD0 + 0x30);
        }
        intptr_t pal = -1;
        if (gga && *gga) pal = *(intptr_t*)((char*)*gga + 66 * 4);
        clog("[good66] landscapetype=%u flags=0x%08X palette=%p (basePal=%p baseGood=%p)\n",
             lt, fl, (void*)pal, *gga, *ggt);
    }

    // Patch table 0x512750 (carry render): entry for type 19 (coal) <- copy from type 20 (iron, known-good)
    if (!g_tablePatched) {
        void** tbl = (void**)0x512750;
        if (tbl && *tbl) {
            char* base = (char*)*tbl;
            char* e19 = base + 19 * 0x184;
            char* e20 = base + 20 * 0x184;
            if (e20[0] != 0) {
                memcpy(e19, e20, 0x184);
                *(uint32_t*)(e19 + 0x10) = 66;
                clog("[table] patched type19 from type20: first=%d good=%u\n", e19[0], *(uint32_t*)(e19+0x10));
                g_tablePatched = true;
            } else {
                // tablica zaladowana - policz wypelnione wpisy
                int filled = 0;
                for (int t = 0; t < 88; t++) if (base[t * 0x184] != 0) filled++;

                // jesli typ 19 pusty a tablica ma cos -> zaladuj recznie (kopiuj z typu 0)
                if (filled > 0 && e19[0] == 0) {
                    char* e0 = base + 0 * 0x184;
                    memcpy(e19, e0, 0x184);
                    *(uint32_t*)(e19 + 0x10) = 66;
                    clog("[table] MANUAL PATCH type19: first=%d good=%u +0x04=%u (copied from type0)\n",
                         (unsigned char)e19[0], *(uint32_t*)(e19+0x10), *(uint32_t*)(e19+0x04));
                    g_tablePatched = true;
                } else if (e19[0] != 0) {
                    g_tablePatched = true;
                }
                // log co 5000 dla diag
                static uint64_t tb_cnt = 0;
                if (++tb_cnt % 5000 == 0) {
                    int first_filled = -1;
                    for (int t = 0; t < 88; t++) if (base[t * 0x184] != 0) { first_filled = t; break; }
                    clog("[table] (call %llu) base=%p filled=%d first_filled=%d entry19_first=%d entry20_first=%d\n",
                         (unsigned long long)tb_cnt, base, filled, first_filled, (unsigned char)e19[0], (unsigned char)e20[0]);
                }
            }
        } else if (!g_tablePatched) {
            static bool logged = false;
            if (!logged) { logged = true; clog("[table] base ptr NULL (0x512750=%p)\n", *tbl); }
        }
    }
    return r;
}

// ============================================================================
// Detour: FUN_0045c94b (0x45C94B) - lookup carry animation slot for good.
// If good=66 (coal) not found in 4 slots, populate empty slot and return it.
// ============================================================================
static int __thiscall hook_carry_lookup_45c94b(void* self, int good)
{
    g_carryLookupCalls++;
    
    int* slots = (int*)((char*)self + 0xAF4);  // [0]=good0, [1]=count0, [2]=good1, [3]=count1, ...
    
    // log ALL calls
    if (good == 66 || g_carryLookupCalls < 20) {
        clog("[carryLookup] #%d unit=%p good=%d slots: ", g_carryLookupCalls, self, good);
        for (int i = 0; i < 4; i++) {
            clog("%d:(g=%d c=%d) ", i, slots[i*2], slots[i*2+1]);
        }
        clog("\n");
    }
    
    for (int i = 0; i < 4; i++) {
        if (slots[i * 2] == good && slots[i * 2 + 1] >= 1) {
            return i;  // found
        }
    }
    // not found - if coal (66), populate first empty slot
    if (good == 66) {
        for (int i = 0; i < 4; i++) {
            if (slots[i * 2] == 0) {  // empty slot
                slots[i * 2] = 66;
                slots[i * 2 + 1] = 100;  // count = 100 (required by FUN_0045caa8)
                clog("[carrySlot] populated slot %d for coal (unit=%p)\n", i, self);
                return i;
            }
        }
    }
    return -1;  // not found, no empty slot
}

// ============================================================================
// Detour: FUN_0046b621 (0x46B621) - main action loop.
// Naprawa animacji niesienia węgla: dla smolarza niosącego węgiel,
// tymczasowo zerujemy +0xAD4 (blokuje ścieżkę kat 5), wypełniamy slot carry
// (+0xAF4/+0xAF8, count=100) i ustawiamy +0xAD0=66. Oryginał wtedy przechodzi
// przez FUN_0045C94b → FUN_0045caa8 → FUN_0045c62b → animacja niesienia.
// Po powrocie przywracamy +0xAD4 (dostawa musi działać dalej).
// ============================================================================
static void __fastcall hook_action_loop_46b621(void* self, void* edx, int param_1)
{
    // Zabezpieczenie: self == nullptr podczas inicjalizacji gry
    if (self == nullptr) {
        o_action_loop_46b621(self, param_1);
        return;
    }

    g_actionLoopCalls++;
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);
    uint32_t ad0 = *(uint32_t*)((char*)self + 0xAD0);
    uint32_t ad4 = *(uint32_t*)((char*)self + 0xAD4);
    bool saved_ad4 = false;
    uint32_t orig_ad4 = 0;

    // Logowanie każdego smolarza (diagnostyka)
    if (job == JOB_SMOLARZ) {
        clog("[anim] SMOLARZ unit=%p ad0=%u ad4=%u param=%d\n", self, ad0, ad4, param_1);
    }

    if (job == JOB_SMOLARZ && (ad0 == GOOD_COAL || ad4 == GOOD_COAL)) {
        orig_ad4 = ad4;
        saved_ad4 = true;

        // Wypełnij slot carry dla węgla (good=66, count=100)
        int* slots = (int*)((char*)self + 0xAF4);
        int empty = -1;
        bool already = false;
        for (int i = 0; i < 4; i++) {
            if (slots[i * 2] == GOOD_COAL && slots[i * 2 + 1] >= 1) { already = true; break; }
            if (slots[i * 2] == 0 && empty < 0) empty = i;
        }
        if (!already && empty >= 0) {
            slots[empty * 2] = GOOD_COAL;
            slots[empty * 2 + 1] = 100;
            clog("[anim] slot %d wypełniony dla węgla (unit=%p)\n", empty, self);
        }

        // Ustaw +0xAD0=66
        if (ad0 != GOOD_COAL) {
            *(uint32_t*)((char*)self + 0xAD0) = GOOD_COAL;
        }

        // Zeruj +0xAD4 żeby ścieżka kat 5 była osiągalna (oryginał ma +0xAD4!=0 → idzie do dostawy)
        *(uint32_t*)((char*)self + 0xAD4) = 0;

        clog("[anim] przygotowano węgiel: ad0=%u ad4=0 (unit=%p)\n",
             *(uint32_t*)((char*)self + 0xAD0), self);
    }

    // call original via MinHook trampoline (avoids recursion)
    o_action_loop_46b621(self, param_1);

    // Przywróć +0xAD4 jeśli był zapisany
    if (saved_ad4) {
        *(uint32_t*)((char*)self + 0xAD4) = orig_ad4;
    }
}

// ============================================================================
// Detour: 0x46B696 - wywoluje 0x42D575 (carry render) gdy [unit+0xAD4]==0.
// To jest BRAMA do carry render. Logujemy, czy smolarz tutaj trafia.
// ============================================================================
static void __fastcall hook_gate_46b696(void* self, void* edx, int a)
{
    // Zabezpieczenie: self == nullptr podczas inicjalizacji gry
    if (self == nullptr) {
        // wywolujemy oryginalna logike bez trampoliny (nie ma o_gate_46b696)
        // 0x46B696 to wewnetrzna brama, nie ma oryginalnej funkcji do wywolania
        // tylko sprawdzamy warunek i ewentualnie wywolujemy carry_render przez trampoline
        uint32_t ad4 = 0;  // nie wiemy, zakladamy 0
        if (ad4 == 0 && o_carry_render_42d575 != nullptr) {
            o_carry_render_42d575(self, a);
        }
        return;
    }

    // self = unit (ESI), a = param (push edx w caller)
    // sprawdzamy [self+0xAD4] - czy == 0?
    uint32_t ad4 = *(uint32_t*)((char*)self + 0xAD4);
    uint32_t ad0 = *(uint32_t*)((char*)self + 0xAD0);
    if (ad0 == 66) { // tylko wegiel
        clog("[gate46B696] unit=%p ad4=%u ad0=%u (wegiel!) call_carry_render=%s\n",
             self, ad4, ad0, (ad4 == 0) ? "TAK (ad4==0)" : "NIE (ad4!=0)");
    }
    // oryginalna logika: if (ad4 == 0) call 0x42D575
    if (ad4 == 0 && o_carry_render_42d575 != nullptr) {
        o_carry_render_42d575(self, a);
    }
}

// ============================================================================
// Detour: FUN_004760BF - inicjacja podniesienia/niesienia dobra przez jednostke.
// SYGNATURA: thiscall, ZERO argumentow stosu (konczy sie `ret`, nie `ret N`).// TYLKO LOG - zero modyfikacji stanu gry (poprzednia wersja z 4 arg. rozjechala
// stos i powodowala crash przy starcie).
// ============================================================================
static void __thiscall hook_pickup_4760bf(void* self)
{
    if (self == nullptr) { o_pickup_4760bf(self); return; }

    uint32_t sel     = *(uint32_t*)((char*)self + 0x1C);
    uint32_t job     = *(uint32_t*)((char*)self + 0x18);
    uint32_t atomic_ = *(uint32_t*)((char*)self + 0x0C);
    uint32_t ad0     = *(uint32_t*)((char*)self + 0xAD0);
    uint32_t ad4     = *(uint32_t*)((char*)self + 0xAD4);

    o_pickup_4760bf(self);

    // logujemy tylko wybrane dobra (wegiel) albo pierwsze 30 wywolan dowolnych
    static int nPickup = 0;
    nPickup++;
    if (sel == GOOD_COAL || ad4 == GOOD_COAL || nPickup <= 30) {
        clog("[pickup] unit=%p sel=%u job=%u atomic=%u | PRZED ad0=%u ad4=%u | PO ad0=%u ad4=%u\n",
             self, sel, job, atomic_, ad0, ad4,
             *(uint32_t*)((char*)self + 0xAD0), *(uint32_t*)((char*)self + 0xAD4));
    }
}

// ============================================================================
// Detour: FUN_0042CEA6 - zwraca pare klatek animacji niesienia.
// SYGNATURA: thiscall, ZERO argumentow stosu, zwraca int*.
//   - jednostka W budynku: klatki z rekordu budynku (0x54C) / 0x437851 / 0x4411CA
//   - jednostka POZA budynkiem: [0x510BF0] + [unit+0xC]*0x58 + 0x12  <- para short
// To jest miejsce, ktore decyduje, czy niesione dobro ma animacje.
// TYLKO LOG.
// ============================================================================
static int* __thiscall hook_carry_frames_42cea6(void* self)
{
    if (self == nullptr) return o_carry_frames_42cea6(self);

    uint32_t ad4 = *(uint32_t*)((char*)self + 0xAD4);
    uint32_t ad0 = *(uint32_t*)((char*)self + 0xAD0);

    int* ret = o_carry_frames_42cea6(self);

    // logujemy tylko gdy jednostka cos niesie (ad4 != 0) - inaczej zalew logu
    if (ad4 == 0) return ret;

    // przy pierwszym niesieniu zrzucamy tabele renderu (budowana po zaladowaniu danych)
    dump_carry_table_once();

    // deduplikacja: (unit, ad4, atomic, wartosc) - max 96 roznych kombinacji
    uint32_t atomic_ = *(uint32_t*)((char*)self + 0x0C);
    uint32_t job     = *(uint32_t*)((char*)self + 0x18);
    uint16_t v0 = ret ? *(uint16_t*)((char*)ret + 0) : 0xFFFF;
    uint16_t v1 = ret ? *(uint16_t*)((char*)ret + 2) : 0xFFFF;

    struct Key { void* u; uint32_t ad4, atomic_, job; uint16_t a, b; };
    static Key seen[96];
    static int nSeen = 0;
    Key k = { self, ad4, atomic_, job, v0, v1 };
    for (int i = 0; i < nSeen; i++) {
        if (seen[i].u == k.u && seen[i].ad4 == k.ad4 && seen[i].atomic_ == k.atomic_
            && seen[i].job == k.job && seen[i].a == k.a && seen[i].b == k.b) return ret;
    }
    if (nSeen < 96) seen[nSeen++] = k;

    uint32_t base = *(uint32_t*)0x510BF0;
    clog("[frames] unit=%p job=%u atomic=%u ad0=%u ad4=%u -> ret=%p (base=0x%08X +%u*0x58+0x12) v0=%u v1=%u%s\n",
         self, job, atomic_, ad0, ad4, ret, base, atomic_, v0, v1,
         (v0 == 0 && v1 == 0) ? "  <<< PUSTE (brak animacji!)" : "");
    return ret;
}

// ============================================================================
// Detour: FUN_0045D14F - szuka wariantu animacji niesienia (thiscall, 2 arg., ret 8).
// TYLKO LOG zwrotki: jesli dla wegla zwraca 0, to lookup animacji nie znajduje wpisu.
// ============================================================================
static bool __thiscall hook_anim_lookup_45d14f(void* self, short* a, short* b)
{
    if (self == nullptr) return o_anim_lookup_45d14f(self, a, b);

    uint32_t ad4 = *(uint32_t*)((char*)self + 0xAD4);
    short ia = a ? *a : -1, ib = b ? *b : -1;

    bool r = o_anim_lookup_45d14f(self, a, b);

    static int n = 0; n++;
    static int nCoal = 0;
    if (ad4 == GOOD_COAL) nCoal++;
    if ((ad4 == GOOD_COAL && nCoal <= 60) || n <= 40) {
        clog("[d14f] ad4=%u in=(%d,%d) -> ret=%d%s\n", ad4, ia, ib, (int)r,
             (ad4 == GOOD_COAL && !r) ? "  <<< WEGIEL: BRAK WARIANTU" : "");
    }
    return r;
}

// ============================================================================
// Detour: FUN_0045C23E - wlasciwy setup sprite'a niesienia (thiscall, 2 arg., ret 8).
// TYLKO LOG zwrotki: ret=0 oznacza, ze animacja NIE zostala ustawiona.
// ============================================================================
static bool __thiscall hook_anim_setup_45c23e(void* self, short* a, short* b)
{
    if (self == nullptr) return o_anim_setup_45c23e(self, a, b);

    uint32_t ad4 = *(uint32_t*)((char*)self + 0xAD4);
    short ia = a ? *a : -1, ib = b ? *b : -1;

    bool r = o_anim_setup_45c23e(self, a, b);

    static int n = 0; n++;
    static int nCoal = 0;
    if (ad4 == GOOD_COAL) nCoal++;
    if ((ad4 == GOOD_COAL && nCoal <= 60) || n <= 40) {
        clog("[c23e] ad4=%u in=(%d,%d) -> ret=%d stan368=%u%s\n", ad4, ia, ib, (int)r,
             *(uint32_t*)((char*)self + 0x368),
             (ad4 == GOOD_COAL && !r) ? "  <<< WEGIEL: SETUP ODRZUCONY" : "");
    }
    return r;
}

// ============================================================================
// Jednorazowy zrzut tabeli renderu niesionego dobra (0x512750, stride 0x184).
// entry+0x00 = flaga "wpis istnieje", entry+0x10 = good.
// To ta tabela decyduje, czy niesiony przedmiot jest w ogole rysowany.
// ============================================================================
static void dump_carry_table_once()
{
    static bool done = false;
    if (done) return;
    done = true;

    uint32_t base = *(uint32_t*)0x512750;
    clog("[table] base=0x%08X (0x512750)\n", base);
    if (base == 0) { clog("[table] BRAK TABLICY\n"); return; }

    for (int t = 0; t < 24; t++) {
        unsigned char* e = (unsigned char*)(base + (uint32_t)t * 0x184);
        clog("[table] type %2d: f00=%u f04=%u f08=%u f0C=%u good10=%u\n",
             t, *(uint32_t*)(e + 0x00), *(uint32_t*)(e + 0x04),
             *(uint32_t*)(e + 0x08), *(uint32_t*)(e + 0x0C),
             *(uint32_t*)(e + 0x10));
    }

    // DIAG: read DAT_00569274 (render context) fields
    uint32_t rc = *(uint32_t*)0x569274;
    clog("[diag] DAT_00569274 = 0x%08X\n", rc);
    if (rc != 0) {
        clog("[diag] *rc (tribe?) = %u, rc+4 (mode?) = %u, rc+0xe1 = %u\n",
             *(uint32_t*)rc, *(uint32_t*)(rc+4), *(uint8_t*)(rc+0xe1));
    }

    // FIX: type 19 (coal pile, landscapetype=19) jest pusty -> niesiony wegiel nie jest rysowany.
    // Ustawiamy first=1, f04=2, f08=19 (type index), f0C=133 (jak typy 5-16), good10=66 (carried_good dla węgla).
    unsigned char* e19 = (unsigned char*)(base + 19u * 0x184);
    if (true) {  // FORCE: always patch type 19 (was skipping due to "juz wypelniony")
        *(uint32_t*)(e19 + 0x00) = 1;   // first = 1 (wpis istnieje)
        *(uint32_t*)(e19 + 0x04) = 0;   // f04 = 0 (tribe 0, z diag: *DAT_00569274=0)
        *(uint32_t*)(e19 + 0x08) = 19;  // f08 = type index (19)
        *(uint32_t*)(e19 + 0x0C) = 133; // f0C = 133 (jak typy 5-16)
        *(uint32_t*)(e19 + 0x10) = GOOD_COAL;  // good = 66 (wegiel)
        clog("[table] FIX type 19 (coal): first=1 f04=2 f08=19 f0C=133 good=66\n");
    } else {
        clog("[table] type 19 juz wypelniony (first=%u good=%u)\n",
             *(uint32_t*)(e19 + 0x00), *(uint32_t*)(e19 + 0x10));
    }
}
static void __thiscall hook_carry_render_42d575(void* self, int param)
{
    uint32_t carried = *(uint32_t*)((char*)self + 0xAD0);
    uint32_t job = *(uint32_t*)((char*)self + U_JOB);
    uint32_t htype = house_type_of(self);
    if (carried == GOOD_COAL || job == JOB_SMOLARZ || param == GOOD_COAL) {
        clog("[carry] unit=%p job=%u htype=%u carried=%u param=%d ad4=%u\n",
             self, job, htype, carried, param, *(uint32_t*)((char*)self + 0xAD4));
    }
    o_carry_render_42d575(self, param);
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
    if (job == JOB_SMOLARZ || actionId == 6 || actionId == 0x16 || param == (int32_t)GOOD_COAL) {
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
// Hook: kategoryzacja dobra (FUN_0045CBBE) - passthrough (kategoria wynika z grup w FUN_004a82bb)
static int __cdecl hook_categorize(int good)
{
    return o_categorize(good);
}

// ============================================================================
// Hook: FUN_00419587 (0x419587) - wymagaj qty > 0 w panelu HQ max surowce
//
// Oryginał zwraca 1 jesli rec[good*0x14+4]!=0 LUB rec[good*0x14+0xc]!=0.
// W panelu HQ (zakladka "max surowce", caller w FUN_004c3ea4, this = DAT_005116d4)
// chcemy pokazywac dobro TYLKO gdy ilosc > 0 (pole +0xc). W innych miejscach
// zachowanie niezmienione. Sprawdzamy self zamiast return address, bo MinHook
// podmienia return address na trampoline.
// ============================================================================
static uint32_t __fastcall hook_0x419587_qty(void* self, void* edx, int good)
{
    // NIC NIE FILTRUJEMY. Panel HQ "najwieksza ilosc surowcow" nie korzysta z tej
    // funkcji - patrz .ai/docs/RE-ANALIZA-PANEL-HQ-MAX-SUROWCOW.md.
    // Hook pozostaje jako miejsce na przyszla diagnostyke (pass-through).
    (void)self; (void)edx; (void)good;
    return o_0x419587_qty ? o_0x419587_qty(self, edx, good) : 0;
}

// ============================================================================
// Detour: FUN_0047e381 - rysowanie ikony dobra w panelu HQ / wierszu zapasu.
// Dla good 66 (wegiel) przekierowujemy na good 3 (kamień), ponieważ good 66
// nie ma własnego zasobu gfxgood w ls_goods.bmd, a good 3 (good_stone) ma.
// ============================================================================
static void* __fastcall hook_draw_good_icon(void* self, int good)
{
    // Dla węgla (good 66) użyj kamienia (good 3), który ma prawidłowy zasób
    if (good == GOOD_COAL) good = 3;
    return o_draw_good_icon(self, good);
}

// ============================================================================
// Globalna mapa good->kategoria z INI
static std::unordered_map<uint32_t,uint32_t> g_goodCategoryMap;
static bool g_catIniLoaded = false;

static void LoadGoodCategoriesIni()
{
    const char* path = "CN.PLMOD\\types\\goodcategories.ini";
    FILE* f = fopen(path, "r");
    if (!f) { clog("[cat] Nie mozna wczytac %s\n", path); return; }
    char line[256];
    bool inSec = false;
    while (fgets(line, sizeof(line), f)) {
        // trim
        char* p = line;
        while (*p==' '||*p=='\t') p++;
        if (*p=='[') {
            if (strncmp(p, "[goodcategories]", 16)==0) inSec=true; else inSec=false;
            continue;
        }
        if (!inSec) continue;
        if (*p=='\0'||*p==';'||*p=='#'||*p=='\n'||*p=='\r') continue;
        char* eq = strchr(p, '=');
        if (!eq) continue;
        *eq = '\0';
        uint32_t good = (uint32_t)atoi(p);
        uint32_t cat = (uint32_t)atoi(eq+1);
        if (cat <= 6) {
            g_goodCategoryMap[good] = cat;
            clog("[cat] INI: good=%u -> kategoria %u\n", good, cat);
        }
    }
    fclose(f);
    g_catIniLoaded = true;
    clog("[cat] Wczytano %u wpisow z %s\n", (uint32_t)g_goodCategoryMap.size(), path);
}

// Hook: budowa listy goods dla kategorii (FUN_004a82bb) - dynamicznie z INI
static void __fastcall hook_catbuild(void* self, void* edx)
{
    o_catbuild(self, edx);
    if (!g_catIniLoaded) return;
    for (auto& kv : g_goodCategoryMap) {
        uint32_t good = kv.first;
        uint32_t cat = kv.second;
        if (cat > 6) continue;
        // Kategoria 0 (self+0x180) NIE jest lista reczna - to grupa "najwieksza
        // ilosc surowcow" budowana i sortowana przez FUN_004a847a (malejaco,
        // tylko qty != 0). Dopisanie tam dobra psuje sort i pokazuje je przy 0.
        // Wlaczenie dobra 66 do tej grupy robi patch limitu w FUN_004a847a.
        if (cat == 0) continue;
        int base = 0x180 + (int)cat * 0x38;
        int* slots = (int*)((char*)self + base);
        bool found = false;
        for (int i = 0; i < 14; i++) {
            if (slots[i] == (int)good) { found = true; break; }
        }
        if (found) continue;
        for (int i = 0; i < 14; i++) {
            if (slots[i] == 0) {
                slots[i] = (int)good;
                clog("[catbuild] added good %u to category %u slot %d\n", good, cat, i);
                break;
            }
        }
    }
}

// ============================================================================
// Hook: ustawia can_produce[66]=1 po kazdym wywolaniu 0x44a0d9 (dispatcher produkcji)
static void __fastcall hook_sched_44a0d9(void* self, void* edx)
{
    if (o_sched_44a0d9) o_sched_44a0d9(self, edx);
    if (self) {
        *(unsigned char*)((char*)self + U_CANPROD + GOOD_COAL) = 1;
    }
}

// ============================================================================
// DIAGNOSTYKA WCZYTANIA ZAPISU (2026-10-28)
//
// Cel: ustalic, DLACZEGO singleton gsmx (DAT_005116d4) jest NULL w chwili
// rysowania budynku (crash EIP=0x4B7574, AV READ @ 0).
// Hipotezy do rozstrzygniecia:
//   H1: FUN_0040704b (INIT) nie zostal wywolany po ostatnim FUN_00407291 (CLEANUP)
//   H2: INIT byl, ale operator_new(0x740) zwrocil NULL (brak pamieci)
//   H3: loader zapisu (FUN_00425ec5) nie doszedl do chunku "gsmx"
//   H4: ktos wywoluje CLEANUP w trakcie gry (poza sciezka loadera)
//
// Zapis WYLACZNIE do logs\cnmod_diag.log (maly, czyszczony przy starcie procesu).
// Zero modyfikacji stanu gry poza jednym wyjatkiem: hook_draw_building pomija
// rysowanie budynku, gdy gsmx == NULL - tylko po to, by nie tracic przebiegu.
// ============================================================================

static FILE* g_diag = nullptr;
static uint64_t g_nDiagDrawSkip = 0;
static uint64_t g_nDiagChunk = 0;

static void dlog(const char* fmt, ...)
{
    if (!g_diag) return;
    va_list ap;
    va_start(ap, fmt);
    vfprintf(g_diag, fmt, ap);
    va_end(ap);
    fflush(g_diag);
}

static void diag_open()
{
    if (g_diag) return;
    g_diag = fopen("logs\\cnmod_diag.log", "w");
    if (g_diag) {
        dlog("[diag] ===== start PID=%lu tick=%llu =====\n",
             (unsigned long)GetCurrentProcessId(),
             (unsigned long long)GetTickCount64());
    }
}

static void diag_close()
{
    if (!g_diag) return;
    dlog("[diag] ===== koniec tick=%llu (pominiete rysowania=%llu, chunki=%llu) =====\n",
         (unsigned long long)GetTickCount64(),
         (unsigned long long)g_nDiagDrawSkip, (unsigned long long)g_nDiagChunk);
    fclose(g_diag);
    g_diag = nullptr;
}

// 0x40704B - globalna inicjalizacja swiata (tworzy m.in. gsmx)
typedef void (__cdecl *FnWorldInit)(short, short, char, void*, unsigned char);
static FnWorldInit o_world_init = nullptr;

static void __cdecl hook_world_init(short w, short h, char p3, void* p4, unsigned char p5)
{
    void* ra = __builtin_return_address(0);
    void* gsmx_before = *(void**)VA_DAT_GSMX;
    unsigned char flag = *(unsigned char*)VA_DAT_WORLD_FLAG;
    dlog("[world] INIT wejscie ra=%p args=(%d,%d,%d,%p,%u) flag=%u gsmx=%p\n",
         ra, (int)w, (int)h, (int)p3, p4, (unsigned)p5, (unsigned)flag, gsmx_before);
    if (o_world_init) o_world_init(w, h, p3, p4, p5);
    dlog("[world] INIT wyjscie flag=%u gsmx=%p\n",
         (unsigned)*(unsigned char*)VA_DAT_WORLD_FLAG, *(void**)VA_DAT_GSMX);
}

// 0x407291 - cleanup swiata (niszczy m.in. gsmx); logujemy KTO wola
typedef void (__cdecl *FnWorldCleanup)();
static FnWorldCleanup o_world_cleanup = nullptr;

static void __cdecl hook_world_cleanup()
{
    void* ra = __builtin_return_address(0);
    dlog("[world] CLEANUP wejscie ra=%p flag=%u gsmx=%p\n",
         ra, (unsigned)*(unsigned char*)VA_DAT_WORLD_FLAG, *(void**)VA_DAT_GSMX);
    if (o_world_cleanup) o_world_cleanup();
    dlog("[world] CLEANUP wyjscie flag=%u gsmx=%p\n",
         (unsigned)*(unsigned char*)VA_DAT_WORLD_FLAG, *(void**)VA_DAT_GSMX);
}

// 0x4190AE - tworzenie singletona gsmx (thiscall: ECX = this)
typedef void* (__fastcall *FnGsmxNew)(void*, void*);
static FnGsmxNew o_gsmx_new = nullptr;

static void* __fastcall hook_gsmx_new(void* self, void* edx)
{
    void* r = o_gsmx_new ? o_gsmx_new(self, edx) : nullptr;
    dlog("[gsmx] NEW self=%p ret=%p -> DAT=%p\n", self, r, *(void**)VA_DAT_GSMX);
    return r;
}

// 0x41912C - load-constructor gsmx z zapisu (thiscall, 1 arg. stosu, ret 4)
typedef void* (__fastcall *FnGsmxLoad)(void*, void*, void*);
static FnGsmxLoad o_gsmx_load = nullptr;

static void* __fastcall hook_gsmx_load(void* self, void* edx, void* reader)
{
    int mode = reader ? *(int*)((char*)reader + 0x10) : -1;
    dlog("[gsmx] LOAD wejscie self=%p reader=%p tryb(param_1[4])=%d\n", self, reader, mode);
    void* r = o_gsmx_load ? o_gsmx_load(self, edx, reader) : nullptr;
    dlog("[gsmx] LOAD wyjscie DAT=%p\n", *(void**)VA_DAT_GSMX);
    return r;
}
// 0x425EC5 - loader zapisu: cdecl(reader, uchar)
// Naprawa przyczyny crashu ladowania zapisu:
//   loader wywoluje FUN_00407291() (cleanup) na starcie, niszczac wszystkie singletony
//   (gsmx, DAT_005116E4 i inne). Niektóre zapisy nie zawieraja chunkow odtwarzajacych
//   te singletony, wiec po loadzie sa NULL i gra crashuje przy renderowaniu.
// Rozwiazanie: po zakonczeniu loadera, jesli kluczowe singletony sa NULL,
// tymczasowo zerujemy flague swiata i wywolujemy FUN_0040704b (tworzy wszystkie
// singletony od nowa, bez ponownego cleanup).
typedef void (__cdecl *FnSaveLoader)(int*, unsigned char);
static FnSaveLoader o_save_loader = nullptr;

static void __cdecl hook_save_loader(int* reader, unsigned char mode)
{
    void* ra = __builtin_return_address(0);
    dlog("[load] START reader=%p mode=%u ra=%p flag=%u gsmx=%p\n",
         reader, (unsigned)mode, ra,
         (unsigned)*(unsigned char*)VA_DAT_WORLD_FLAG, *(void**)VA_DAT_GSMX);
    if (o_save_loader) o_save_loader(reader, mode);
    // --- naprawa przyczyny: odtworz singletony zniszczone przez cleanup w loaderze ---
    unsigned char flag = *(unsigned char*)VA_DAT_WORLD_FLAG;
    void* gsmx = *(void**)VA_DAT_GSMX;
    void* dat_e4 = *(void**)0x005116E4;
    dlog("[load] END flag=%u gsmx=%p dat_e4=%p\n", flag, gsmx, dat_e4);
    if (flag == 1 && (gsmx == nullptr || dat_e4 == nullptr)) {
        // Tymczasowo zeruj flage, zeby FUN_0040704b pominiel galez z cleanup
        unsigned char* flag_ptr = (unsigned char*)VA_DAT_WORLD_FLAG;
        *flag_ptr = 0;
        typedef void (__cdecl *FnWorldInit)(short, short, char, void*, unsigned char);
        static FnWorldInit p_world_init = (FnWorldInit)0x0040704B;
        dlog("[load] REPAIR wywoluje FUN_0040704b (gsmx=%p, dat_e4=%p)\n", gsmx, dat_e4);
        p_world_init(250, 250, 0, nullptr, 0);
        dlog("[load] REPAIR po FUN_0040704b: gsmx=%p, dat_e4=%p, flag=%u\n",
             *(void**)VA_DAT_GSMX, *(void**)0x005116E4, (unsigned)*flag_ptr);
    }
}

// 0x42A28D - odczyt naglowka kolejnego chunku ("hoix" + 4-znakowy class id)
// thiscall(reader) -> bool; [reader+0x0C] = class id po odczycie
typedef unsigned char (__fastcall *FnChunkRead)(void*, void*);
static FnChunkRead o_chunk_read = nullptr;

static unsigned char __fastcall hook_chunk_read(void* self, void* edx)
{
    unsigned char r = o_chunk_read ? o_chunk_read(self, edx) : 0;
    if (r && self) {
        unsigned int cls = *(unsigned int*)((char*)self + 0x0C);
        char tag[5];
        tag[0] = (char)(cls & 0xFF);
        tag[1] = (char)((cls >> 8) & 0xFF);
        tag[2] = (char)((cls >> 16) & 0xFF);
        tag[3] = (char)((cls >> 24) & 0xFF);
        tag[4] = 0;
        bool printable = true;
        for (int i = 0; i < 4; ++i) {
            unsigned char c = (unsigned char)tag[i];
            if (c < 0x20 || c > 0x7E) printable = false;
        }
        dlog("[load] chunk #%llu class=0x%08X (%s) off=0x%X\n",
             (unsigned long long)++g_nDiagChunk, cls,
             printable ? tag : "????", (unsigned)*(unsigned int*)((char*)self + 0x28));
    }
    return r;
}

// 0x4B74C8 - rysowanie budynku (thiscall 2 arg., ret 8); uzywa gsmx bez null-checku.
// Zabezpieczenie diagnostyczne: gdy gsmx == NULL -> pomijamy rysowanie (bez crashu).
typedef void (__fastcall *FnDrawBuilding)(void*, void*, void*, void*);
static FnDrawBuilding o_draw_building = nullptr;

static void __fastcall hook_draw_building(void* self, void* edx, void* a, void* b)
{
    void* gsmx = *(void**)VA_DAT_GSMX;
    if (!gsmx) {
        ++g_nDiagDrawSkip;
        if (g_nDiagDrawSkip <= 40) {
            dlog("[draw] POMINIETE 4B74C8 self=%p a=%p b=%p: gsmx=NULL (skip #%llu)\n",
                 self, a, b, (unsigned long long)g_nDiagDrawSkip);
        }
        return;
    }
    if (o_draw_building) o_draw_building(self, edx, a, b);
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

// ============================================================================
// Detour: FUN_00412b62 - inicjalizuje tabelę 0x510c60 (landscapetype -> good ID)
// Oryginał wypełnia wpisy tylko dla dóbr 0-55. Po oryginale wypełniamy mapowanie
// z pliku CN.PLMOD/types/landscape_good_map.ini (można dodać nowe surowce
// bez przebudowy DLL).
// ============================================================================
static void __fastcall hook_init_landscape_table(void* self, void* edx)
{
    o_init_landscape_table(self, edx);
    // Po oryginalnej inicjalizacji wypełniamy mapowanie landscapetype -> good
    // z pliku CN.PLMOD/types/landscape_good_map.ini
    if (g_landscapeMapLoaded) {
        for (auto& kv : g_landscapeGoodMap) {
            uint32_t lt = kv.first;
            uint32_t good = kv.second;
            *(uint32_t*)(0x510c60 + lt * 4u) = good;
            clog("[lgm] table[%u] = %u (tooltip)\n", lt, good);
        }
    } else {
        clog("[lgm] Mapa nie wczytana - pomijam uzupełnienie tabeli 0x510c60\n");
    }
}

static bool install_hooks()
{
    MH_STATUS st = MH_Initialize();
    if (st != MH_OK && st != MH_ERROR_ALREADY_INITIALIZED) {
        clog("[init] MH_Initialize = %d\n", (int)st);
        return false;
    }
    bool ok = true;

    // Wczytaj mapping kategorii dobra z INI (przed instalacją hooków)
    LoadGoodCategoriesIni();

    // Wczytaj mapowanie landscapetype -> good ID z INI (przed instalacją hooków)
    LoadLandscapeGoodMapIni();

    ok &= install_one("unit_tick(473461)",  VA_UNIT_TICK,  (LPVOID)&hook_unit_tick,  (LPVOID*)&o_unit_tick);
    ok &= install_one("dispatcher(46BAD7)", VA_DISPATCHER, (LPVOID)&hook_dispatcher, (LPVOID*)&o_dispatcher);
    ok &= install_one("potter(46D53A)",     VA_POTTER,     (LPVOID)&hook_potter,     (LPVOID*)&o_potter);
    ok &= install_one("case46BDC1(473695)", VA_CASE46BDC1, (LPVOID)&hook_case46bdc1, (LPVOID*)&o_case46bdc1);
    ok &= install_one("find_owner(43267F)", VA_FIND_OWNER, (LPVOID)&hook_find_owner, (LPVOID*)&o_find_owner);
    ok &= install_one("stock_add(44B910)",  VA_STOCK_ADD,  (LPVOID)&hook_stock_add,  (LPVOID*)&o_stock_add);
    ok &= install_one("gate 42DA65",        VA_GATE_42DA65,(LPVOID)&hook_gate_42da65,(LPVOID*)&o_gate_42da65);
    ok &= install_one("sched 44A0D9",       VA_SCHED_44A0D9,(LPVOID)&hook_sched_44a0d9,(LPVOID*)&o_sched_44a0d9);
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
ok &= install_one("categorize(45CBBE)", VA_CATEGORIZE, (LPVOID)&hook_categorize, (LPVOID*)&o_categorize);
ok &= install_one("catbuild(4A82BB)", VA_CATBUILD, (LPVOID)&hook_catbuild, (LPVOID*)&o_catbuild);
// ok &= install_one("goodicon(47e381)", VA_DRAW_GOOD_ICON, (LPVOID)&hook_draw_good_icon, (LPVOID*)&o_draw_good_icon);
// NIE instalowac detourow 0x4E15B3 / 0x4E162E / 0x42F798 - patrz komentarz przy
// stalych VA_* (zla sygnatura, zwracaly smieci). Ikona węgla = patch 0x0015EB2.
ok &= install_one("qty>0(419587)", VA_0x419587_QTY, (LPVOID)&hook_0x419587_qty, (LPVOID*)&o_0x419587_qty);
// ------ diagnostyka wczytywania zapisu (osobny plik logs\\cnmod_diag.log) ------ok &= install_one("world_init(40704B)", VA_WORLD_INIT,   (LPVOID)&hook_world_init,   (LPVOID*)&o_world_init);
ok &= install_one("world_cleanup(407291)", VA_WORLD_CLEANUP, (LPVOID)&hook_world_cleanup, (LPVOID*)&o_world_cleanup);
ok &= install_one("gsmx_new(4190AE)",   VA_GSMX_NEW,   (LPVOID)&hook_gsmx_new,   (LPVOID*)&o_gsmx_new);
ok &= install_one("gsmx_load(41912C)",  VA_GSMX_LOAD,  (LPVOID)&hook_gsmx_load,  (LPVOID*)&o_gsmx_load);
ok &= install_one("save_loader(425EC5)",VA_SAVE_LOADER,(LPVOID)&hook_save_loader,(LPVOID*)&o_save_loader);
ok &= install_one("chunk_read(42A28D)", VA_CHUNK_READ, (LPVOID)&hook_chunk_read, (LPVOID*)&o_chunk_read);
ok &= install_one("draw_building(4B74C8)", VA_DRAW_BUILDING,(LPVOID)&hook_draw_building,(LPVOID*)&o_draw_building);
ok &= install_one("init_landscape_table(412b62)", VA_INIT_LANDSCAPE_TABLE, (LPVOID)&hook_init_landscape_table, (LPVOID*)&o_init_landscape_table);
// ------ koniec diagnostyki ------
// DIAGNOSTYKA ANIMACJI NIESIENIA (2026-10-25) - TYLKO LOG, zero modyfikacji stanu.
// Wlaczamy WYLACZNIE funkcje o ZWERYFIKOWANEJ sygnaturze (thiscall, 0 arg. stosu):
//   0x4760BF (pickup) i 0x42CEA6 (para klatek animacji niesienia).
// NIE hookowac 0x42D575 (1 arg. stosu + `ret` = sprzatanie po stronie wywolujacego)
// ani 0x46B696 (lezy WEWNATRZ FUN_0046B621) - to powodowalo crash.
ok &= install_one("pickup(4760BF)",       VA_PICKUP_4760BF, (LPVOID)&hook_pickup_4760bf, (LPVOID*)&o_pickup_4760bf);
ok &= install_one("carry_frames(42CEA6)", VA_CARRY_FRAMES_42CEA6, (LPVOID)&hook_carry_frames_42cea6, (LPVOID*)&o_carry_frames_42cea6);
ok &= install_one("anim_lookup(45D14F)",  VA_ANIM_LOOKUP_45D14F, (LPVOID)&hook_anim_lookup_45d14f, (LPVOID*)&o_anim_lookup_45d14f);
ok &= install_one("anim_setup(45C23E)",   VA_ANIM_SETUP_45C23E,  (LPVOID)&hook_anim_setup_45c23e,  (LPVOID*)&o_anim_setup_45c23e);
// ok &= install_one("carry_render(42D575)", VA_CARRY_RENDER_42D575, (LPVOID)&hook_carry_render_42d575, (LPVOID*)&o_carry_render_42d575);
// ok &= install_one("gate_46B696",          VA_GATE_46B696,   (LPVOID)&hook_gate_46b696,   (LPVOID*)nullptr);
// ok &= install_one("carry_lookup(45C94B)", VA_CARRY_LOOKUP_45C94B, (LPVOID)&hook_carry_lookup_45c94b, (LPVOID*)nullptr);
// ok &= install_one("action_loop(46B621)", VA_ACTION_LOOP_46B621, (LPVOID)&hook_action_loop_46b621, (LPVOID*)&o_action_loop_46b621);

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
         "[exit] Faza3: set_action=%llu prod_finish=%llu stock_write=%llu\n[exit] carry_lookup calls=%d actionLoop calls=%d\n"
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
          g_carryLookupCalls,
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
        if (g_installed) {
            diag_open();
        }
        break;
    }
    case DLL_PROCESS_DETACH:
        shutdown_hooks();
        diag_close();
        if (g_log) { fclose(g_log); g_log = nullptr; }
        break;
    }
    return TRUE;
}
