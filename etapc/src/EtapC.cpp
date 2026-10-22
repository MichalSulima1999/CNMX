// EtapC.cpp - runtime overlay dla CN.PLMOD.exe
//
// Aplikuje tablice Patch[] z auto-generowanego patches_ext.h (Etap 1+2:
// relokacja tablic per-plemienia aktora + rekord plemienia, stride/limity 0x7F).
// Dodatkowo inicjalizuje MinHook (szkielet pod przyszle hooki).
//
// Budowa/uzytk: EtapC.dll jest wstrzykiwana przez launcher.exe do procesu
// CN.PLMOD.exe; patche aplikuja sie w DllMain (MODE_PROCESS_ATTACH).

#include <windows.h>
#include <tlhelp32.h>
#include <cstdio>
#include "patches_ext.h"

// MinHook (lokalna dystrybucja w .tools/minhook-master)
#include "MinHook.h"

static const char* DLL_NAME = "EtapC.dll";

static void etapc_minhook_init(void)
{
    MH_STATUS st = MH_Initialize();
    if (st != MH_OK) {
        etapc_log("[%s] MinHook MH_Initialize failed: %d\n", DLL_NAME, (int)st);
        return;
    }
    etapc_log("[%s] MinHook initialized\n", DLL_NAME);
    /* Tutaj wstawimy faktyczne hooki funkcji gry w kolejnych etapach. */
}

/* ---- Hook: GetJobString (RVA 0x2F754) --------------------------------
   Gra buduje teksty typu "<nazwa> - <praca>" przez
   strcat(buf, GetJobString(job, 1)). Dla job >= liczby wpisow w tablicy
   tekstow (np. nowy job 56 "Smolarz") GetJobString zwraca NULL i strcat
   sie wywala (AV @0xE549B, strcat(dst, NULL)). Hook loguje job i podstawia
   nazwe zapasowa, wiec brak tekstu nie powoduje juz crashu. To jednoczesnie
   bezpiecznik i sonda diagnostyczna (w logs\etapc.log widac, o jaki job
   i o jaka nazwe gra prosila w chwili wywalenia). */
typedef const char* (__cdecl *t_GetJobString)(int job, int plural);
static t_GetJobString p_GetJobString = NULL;

static const char* job_fallback_name(int job, int plural)
{
    switch (job) {
    case 56: return (plural > 1) ? "Smolarze" : "Smolarz";
    default: return "?";
    }
}

/* licznik brakow nazwy - zeby log nie rosl o tysiace identycznych linii */
static unsigned g_job_null = 0;

static const char* __cdecl hook_GetJobString(int job, int plural)
{
    const char* r = p_GetJobString ? p_GetJobString(job, plural) : NULL;
    if (r == NULL) {
        if (g_job_null < 8 || (g_job_null % 5000) == 0) {
            etapc_log("[EtapC] GetJobString(job=%d,plural=%d)==NULL -> fallback \"%s\" (wystapienie %u)\n",
                      job, plural, job_fallback_name(job, plural), g_job_null + 1);
        }
        ++g_job_null;
        r = job_fallback_name(job, plural);
    }
    return r;
}

static void etapc_install_hooks(void)
{
    BYTE* base = (BYTE*)GetModuleHandleA(NULL);
    void* target = base + 0x2F754;              /* GetJobString */
    MH_STATUS st = MH_CreateHook(target, (LPVOID)&hook_GetJobString, (LPVOID*)&p_GetJobString);
    if (st != MH_OK) {
        etapc_log("[EtapC] MH_CreateHook(GetJobString) failed: %d\n", (int)st);
        return;
    }
    st = MH_EnableHook(target);
    if (st != MH_OK) {
        etapc_log("[EtapC] MH_EnableHook(GetJobString) failed: %d\n", (int)st);
        return;
    }
    etapc_log("[EtapC] hook GetJobString (0x2F754) zainstalowany\n");
}

extern "C" __declspec(dllexport) BOOL WINAPI EtapC_TestExport(void)
{
    return TRUE;
}

/* ================= DIAGNOSTYKA (tymczasowa) ===============================
   Zrzut tablic aktora (stare vs nowe offsety) do logs\dump_etapc.txt.
   Odpowiada na pytanie: gdzie silnik faktycznie TRZYMA dane po uruchomieniu.
   ======================================================================== */
static int drange_ok(const void* p, size_t n)
{
    const BYTE* base = (const BYTE*)p;
    while (n) {
        MEMORY_BASIC_INFORMATION mbi;
        if (VirtualQuery(base, &mbi, sizeof(mbi)) == 0) return 0;
        DWORD pr = mbi.Protect;
        if (pr == 0 || (pr & (PAGE_NOACCESS | PAGE_GUARD))) return 0;
        size_t in = (size_t)((const BYTE*)mbi.BaseAddress + mbi.RegionSize - base);
        if (in == 0) return 0;
        if (in > n) in = n;
        base += in; n -= in;
    }
    return 1;
}

static DWORD WINAPI dump_thread(LPVOID)
{
    int iter = 0;
    for (int i = 0; i < 60; i++) {
        Sleep(4000);
        if (!drange_ok((const void*)0x510BC4, 4)) continue;
        DWORD pool = *(DWORD volatile*)0x510BC4;
        if (pool == 0) continue;

        CreateDirectoryA("logs", NULL);
        const char* mode = (iter == 0) ? "w" : "a";
        FILE* f = fopen("logs\\dump_etapc.txt", mode);
        if (!f) continue;

        fprintf(f, "\n=== DIAG iter %d tick=%lu pool=0x%08X ===\n",
                iter, GetTickCount(), pool);
        if (drange_ok((const void*)pool, 2 * (size_t)NEW_ELEM_SIZE)) {
            static const struct { const char* nm; DWORD off; } OLD_TAB[] = {
                { "goodsA ", 0x1278 }, { "goodsA2", 0x1D4C }, { "housesA", 0x2820 },
                { "housesB", 0x3126 }, { "goodsB ", 0x3C78 },
            };
            static const struct { const char* nm; DWORD off; } NEW_TAB[] = {
                { "goodsA ", NEW_GOODS_A  }, { "goodsA2", NEW_GOODS_A2 },
                { "goodsB ", NEW_GOODS_B  }, { "housesA", NEW_HOUSES_A },
                { "housesB", NEW_HOUSES_B },
            };
            for (int pl = 0; pl < 2; pl++) {
                const BYTE* E = (const BYTE*)pool + (size_t)pl * NEW_ELEM_SIZE;
                fprintf(f, "player %d elem=0x%08X\n", pl, (DWORD)(uintptr_t)E);
                int k;
                for (k = 0; k < 5; k++) {
                    const BYTE* p = E + OLD_TAB[k].off;
                    fprintf(f, "  OLD %s @%04X: ", OLD_TAB[k].nm, OLD_TAB[k].off);
                    for (int j = 0; j < 0x40; j++) fprintf(f, "%02X", p[j]);
                    fprintf(f, "\n");
                }
                for (k = 0; k < 5; k++) {
                    const BYTE* p = E + NEW_TAB[k].off;
                    fprintf(f, "  NEW %s @%04X: ", NEW_TAB[k].nm, NEW_TAB[k].off);
                    for (int j = 0; j < 0x40; j++) fprintf(f, "%02X", p[j]);
                    fprintf(f, "\n");
                }
                /* pasek wierszy (struktura stride): wiersz t = off + t*stride */
                for (int t = 0; t < 4; t++) {
                    const BYTE* pa = E + 0x2820 + t * 0x37;   /* housesA old */
                    const BYTE* pb = E + 0x3126 + t * 0x37;   /* housesB old */
                    const BYTE* pn = E + NEW_HOUSES_A + t * NEW_STRIDE;
                    fprintf(f, "  STRIPE t=%d housesA_old=%02X%02X%02X%02X housesB_old=%02X%02X%02X%02X housesA_new=%02X%02X%02X%02X\n",
                            t, pa[0], pa[1], pa[2], pa[3],
                            pb[0], pb[1], pb[2], pb[3],
                            pn[0], pn[1], pn[2], pn[3]);
                }
                /* konkretne komórki (tribe, sub): stary vs nowy adres */
                {
                    const BYTE* a_old = E + 0x1770;  /* goodsA tribe19 sub0x12 */
                    const BYTE* a_new = E + NEW_GOODS_A + 19 * NEW_STRIDE + 0x12;
                    const BYTE* h_old = E + 0x2A48;  /* housesA tribe10 sub2 */
                    const BYTE* h_new = E + NEW_HOUSES_A + 10 * NEW_STRIDE + 2;
                    const BYTE* b_old = E + 0x3D60;  /* goodsB tribe4 sub8 */
                    const BYTE* b_new = E + NEW_GOODS_B + 4 * NEW_STRIDE + 8;
                    fprintf(f, "  CELL goodsA19/12 old=%02X new=%02X | housesA10/2 old=%02X new=%02X | goodsB4/8 old=%02X new=%02X\n",
                            a_old[0], a_new[0], h_old[0], h_new[0], b_old[0], b_new[0]);
                }
            }
        } else {
            fprintf(f, "  (pool poza zmapowanym zakresem)\n");
        }
        fclose(f);
        iter++;
    }
    return 0;
}

/* ================= REJESTRATOR CRASHY (tymczasowy) =========================
   Loguje kazdy 'prawdziwy' wyjatek (AV i inne fatalne) do logs\crash.txt
   (dopisujac - widac sekwencje redelivery), z bajtami w EIP i stosem ramek.
   Zwraca EXCEPTION_CONTINUE_SEARCH - proces pada normalnie. */
static DWORD crash_seq = 0;
static volatile LONG crash_busy = 0;   /* bariera re-entry: jesli handler sam
                                          bladzi (np. w fprintf), NIE wchodz
                                          ponownie - inaczej zapetla plik */

static void crash_dump_bytes(FILE* f, const void* p, int n)
{
    if (IsBadReadPtr(p, (UINT_PTR)n)) {
        fprintf(f, "<nieczytelne>");
        return;
    }
    const BYTE* b = (const BYTE*)p;
    for (int i = 0; i < n; i++) fprintf(f, "%02X ", b[i]);
}

/* Snapshot danych aktora + listy budynkow [0x569274] - wypisywany w crash_logger
   i w region_sampler, zeby sesje crash vs czysta (NOPATCH) byly porownywalne.
   Wszyatkie odczyty przez drange_ok/pog, wiec nie moze samo AV-ic. */
static void write_actor_snap(FILE* f, DWORD g274, int prefix)
{
    BYTE* base = (BYTE*)GetModuleHandleA(NULL);
    /* pula aktorow: global bezwzgledny 0x510BC4 -> elementy NEW_ELEM_SIZE */
    DWORD poolv = 0;
    if (drange_ok((const void*)0x510BC4, 4))
        poolv = *(DWORD volatile*)0x510BC4;
    fprintf(f, "%*spool@[0x510BC4]=0x%08X\n", prefix, "", poolv);
    static const struct { const char* nm; DWORD off; } OLD_TAB[] = {
        { "goodsA ", 0x1278 }, { "goodsA2", 0x1D4C }, { "housesA", 0x2820 },
        { "housesB", 0x3126 }, { "goodsB ", 0x3C78 } };
    if (poolv && drange_ok((const void*)poolv, (size_t)NEW_ELEM_SIZE)) {
        const BYTE* E = (const BYTE*)poolv;   /* element gracza 0 */
        for (int k = 0; k < 5; k++) {
            fprintf(f, "%*sA0 %s@%04X: ", prefix, "", OLD_TAB[k].nm, OLD_TAB[k].off);
            crash_dump_bytes(f, E + OLD_TAB[k].off, 0x40);
            fprintf(f, "\n");
        }
        fprintf(f, "%*sA0 NEW goodsA@0x%04X: ", prefix, "", NEW_GOODS_A);
        crash_dump_bytes(f, E + NEW_GOODS_A, 0x40);
        fprintf(f, "\n");
    }
    if (g274 && drange_ok((const void*)g274, 0x80)) {
        fprintf(f, "%*s[0x569274]+0x40: ", prefix, "");
        crash_dump_bytes(f, (const BYTE*)g274 + 0x40, 0x40);
        fprintf(f, "\n");
    }
    /* aktor: global 0x510BC4 + jego 4 DWORD-y sasiadow (0x510BC8..) */
    const DWORD* gb = (const DWORD*)0x510BC4;
    size_t gbno = 5;
    if (!drange_ok(gb, gbno * 4)) gbno = 0;
    if (gbno) {
        fprintf(f, "%*sneighbors 0x510BC4: ", prefix, "");
        for (size_t j = 0; j < gbno; j++) fprintf(f, "%08X ", gb[j]);
        fprintf(f, "\n");
    }
}

static void crash_dump_stack(FILE* f, DWORD ebp)
{
    fprintf(f, "  stack:\n");
    BYTE* base = (BYTE*)GetModuleHandleA(NULL);
    for (int i = 0; i < 12 && ebp >= 0x10000 && ebp < 0x80000000; i++) {
        if (IsBadReadPtr((const void*)ebp, 8)) {
            fprintf(f, "    [%d] <koniec ramek>\n", i);
            break;
        }
        DWORD next = *(DWORD*)ebp;
        DWORD ret = *(DWORD*)(ebp + 4);
        DWORD rva = ((BYTE*)ret >= base) ? (DWORD)((BYTE*)ret - base) : (DWORD)-1;
        fprintf(f, "    [%d] ebp=%08X ret=%08X rva=%08X\n", i, ebp, ret, rva);
        if (next <= ebp) break;
        ebp = next;
    }
}

/* Zrzut surowego stosu od ESP + lista kandydatow na adresy powrotne (dwordy
   wskazujace w .text). Pozwala odtworzyc rzeczywisty lancuch wywolan, gdy EBP
   nie jest ramka (funkcje lisciowe CRT). */
static void crash_dump_raw_stack(FILE* f, DWORD esp)
{
    BYTE* base = (BYTE*)GetModuleHandleA(NULL);
    DWORD lo = (DWORD)(uintptr_t)(base + 0x1000);     /* .text start */
    DWORD hi = (DWORD)(uintptr_t)(base + 0xF3000);    /* .text end   */
    fprintf(f, "  rawstack(ESP=0x%08X .. +0x180):\n", esp);
    for (int i = 0; i < 0x180 / 4; i++) {
        DWORD a = esp + (DWORD)i * 4;
        if (IsBadReadPtr((const void*)a, 4)) break;
        DWORD v = *(DWORD*)a;
        if ((i % 4) == 0) fprintf(f, "    %08X:", a);
        fprintf(f, " %08X", v);
        if ((i % 4) == 3) {
            fprintf(f, "  ");
            for (int j = i - 3; j <= i; j++) {
                DWORD av = esp + (DWORD)j * 4;
                if (IsBadReadPtr((const void*)av, 4)) continue;
                DWORD vv = *(DWORD*)av;
                if (vv >= lo && vv < hi) fprintf(f, "[+%02X]->rva%X ", j * 4, vv - (DWORD)(uintptr_t)base);
            }
            fprintf(f, "\n");
        }
    }
    /* globalne wskazniki uzyte w sciezce UI (0x554f3c = obiekt powiadomien) */
    if (!IsBadReadPtr((const void*)0x554f3c, 4)) {
        DWORD g = *(DWORD volatile*)0x554f3c;
        fprintf(f, "  [0x554f3c]=0x%08X", g);
        if (g && !IsBadReadPtr((const void*)g, 16)) {
            DWORD vt = *(DWORD*)g;
            fprintf(f, " vtbl=0x%08X", vt);
        }
        fprintf(f, "\n");
    }
    if (!IsBadReadPtr((const void*)0x554f20, 4)) {
        DWORD g = *(DWORD volatile*)0x554f20;
        fprintf(f, "  [0x554f20]=0x%08X\n", g);
    }
    if (!IsBadReadPtr((const void*)0x5116a0, 4)) {
        DWORD g = *(DWORD volatile*)0x5116a0;
        fprintf(f, "  [0x5116a0]=0x%08X (jobs text mgr)\n", g);
    }
    if (!IsBadReadPtr((const void*)0x511180, 4)) {
        DWORD g = *(DWORD volatile*)0x511180;
        fprintf(f, "  [0x511180]=0x%08X (job table)", g);
        if (g && !IsBadReadPtr((const void*)g, 0x100)) {
            fprintf(f, " jobs[55].name='%s' flags[0x86]=%02X",
                    (const char*)g + 55 * 0x88, ((const unsigned char*)g)[55 * 0x88 + 0x86]);
        }
        fprintf(f, "\n");
    }
}

static LONG WINAPI crash_logger(EXCEPTION_POINTERS* ep)
{
    /* Benignne/debug wyjatki -> nie loguj */
    switch (ep->ExceptionRecord->ExceptionCode) {
    case 0x40010006:          /* OutputDebugString */
    case 0x40010007:          /* OutputDebugStringW */
    case 0x80000003:          /* breakpoint */
    case 0x40000005:
    case 0x406D1388:          /* SetThreadName */
        return EXCEPTION_CONTINUE_SEARCH;
    default:
        break;
    }

    if (InterlockedCompareExchange(&crash_busy, 1, 0) != 0)
        return EXCEPTION_CONTINUE_SEARCH;   /* juz w trakcie logowania - nie re-entruj */

    DWORD seq = InterlockedIncrement(&crash_seq);
    CreateDirectoryA("logs", NULL);
    FILE* f = fopen("logs\\crash.txt", "a");
    if (f) {
        BYTE* base = (BYTE*)GetModuleHandleA(NULL);
        EXCEPTION_RECORD* er = ep->ExceptionRecord;
        CONTEXT* c = ep->ContextRecord;
        DWORD rva = er->ExceptionAddress >= (void*)base
                        ? (DWORD)((BYTE*)er->ExceptionAddress - base) : 0xFFFFFFFF;
        fprintf(f, "=== CRASH #%u code=0x%08X flags=0x%X addr_va=0x%p addr_rva=0x%08X (pid=%lu)\n",
                seq, er->ExceptionCode, er->ExceptionFlags, er->ExceptionAddress, rva,
                GetCurrentProcessId());
        if (er->ExceptionCode == 0xC0000005 && er->NumberParameters >= 2)
            fprintf(f, "  AV: %s @ 0x%08X\n",
                    er->ExceptionInformation[0] ? "WRITE" : "READ",
                    (DWORD)er->ExceptionInformation[1]);
        fprintf(f, "  bajty@EIP: ");
        crash_dump_bytes(f, er->ExceptionAddress, 10);
        fprintf(f, "\n");
        fprintf(f, "  pamiec@0xBD6C0 (fun wokol EIP): ");
        crash_dump_bytes(f, (BYTE*)base + 0xBD6C0, 0x1B0);
        fprintf(f, "\n");
        fprintf(f, "  pamiec@0xC5130 (caller): ");
        crash_dump_bytes(f, (BYTE*)base + 0xC5130, 0x70);
        fprintf(f, "\n");
        {
            /* globala gry siedz a pod adresami BEZWZGLEDNYMI 0x569264..
               0x569274 (= RVA 0x169264.. od bazy) */
            BYTE* gp = (BYTE*)base + 0x169264;
            DWORD g264 = 0, g268 = 0, g26C = 0, g270 = 0, g274 = 0;
            if (drange_ok(gp, 20)) {
                g264 = *(DWORD volatile*)gp;
                g268 = *(DWORD volatile*)(gp + 4);
                g26C = *(DWORD volatile*)(gp + 8);
                g270 = *(DWORD volatile*)(gp + 0xC);
                g274 = *(DWORD volatile*)(gp + 0x10);
            }
            fprintf(f, "  globals: [0x569264]=0x%08X [0x569268]=0x%08X "
                    "[0x56926C]=0x%08X [0x569270]=0x%08X [0x569274]=0x%08X\n",
                    g264, g268, g26C, g270, g274);
            if (drange_ok((void*)g268, 32))
                { fprintf(f, "  @[0x569268]: "); crash_dump_bytes(f, (void*)g268, 32); fprintf(f, "\n"); }
            if (drange_ok((void*)g274, 80))
                { fprintf(f, "  @[0x569274]: "); crash_dump_bytes(f, (void*)g274, 80); fprintf(f, "\n"); }
            write_actor_snap(f, g274, 2);
        }
        fprintf(f, "  @EAX(0x%08X): ", c->Eax);
        crash_dump_bytes(f, (void*)c->Eax, 16);
        fprintf(f, "\n  @ECX: ");
        crash_dump_bytes(f, (void*)c->Ecx, 64);
        fprintf(f, "\n  @ESI: ");
        crash_dump_bytes(f, (void*)c->Esi, 64);
        fprintf(f, "\n");
        fprintf(f, "  EAX=0x%08X EBX=0x%08X ECX=0x%08X EDX=0x%08X\n",
                c->Eax, c->Ebx, c->Ecx, c->Edx);
        fprintf(f, "  ESI=0x%08X EDI=0x%08X EBP=0x%08X ESP=0x%08X\n",
                c->Esi, c->Edi, c->Ebp, c->Esp);
        fprintf(f, "  EIP=0x%08X EFL=0x%08X\n", c->Eip, c->EFlags);
        crash_dump_stack(f, c->Ebp);
        crash_dump_raw_stack(f, c->Esp);
        fclose(f);
    }
    InterlockedExchange(&crash_busy, 0);
    return EXCEPTION_CONTINUE_SEARCH;
}

/* DIAGNOSTYKA: probkownik STATYCZNEGO obrazu runtime (regiony .text wokol
   0xBD6C0, 0xC5100 + globala gry [0x569264..0x569274] + 64 B obiektu listy).
   Czyta TYLKO zmapowane regiony (drange_ok) -> nie moze zapetlic sie w AV.
   Sluzy do porownania builda patched vs czysty (ETAPC_NOPATCH=1). */
static DWORD WINAPI region_sampler(void*)
{
    Sleep(4000);
    DWORD last_hash = 0;
    for (int it = 0; it < 1200; it++) {
        BYTE* base = (BYTE*)GetModuleHandleA(NULL);
        BYTE buf[0x1B0 + 0xC0 + 0x14 + 64 + 4 + 6 * 0x40];
        SIZE_T n1 = 0, n2 = 0, n3 = 0;
        memset(buf, 0, sizeof(buf));
        if (drange_ok(base + 0xBD6C0, 0x1B0)) {
            memcpy(buf, base + 0xBD6C0, 0x1B0);
            n1 = 0x1B0;
        }
        if (drange_ok(base + 0xC5100, 0xC0)) {
            memcpy(buf + 0x1B0, base + 0xC5100, 0xC0);
            n2 = 0xC0;
        }
        if (drange_ok(base + 0x169264, 0x14)) {
            DWORD g = *(DWORD volatile*)(base + 0x169274);
            memcpy(buf + 0x1B0 + 0xC0, base + 0x169264, 0x14);
            if (drange_ok((void*)g, 64))
                memcpy(buf + 0x1B0 + 0xC0 + 0x14, (void*)g, 64);
        }
        /* pula aktorow + element0 (stare offsety tablic, aktywne w A+B) */
        if (drange_ok((const void*)0x510BC4, 4)) {
            DWORD poolv = *(DWORD volatile*)0x510BC4;
            *(DWORD*)(buf + 0x1B0 + 0xC0 + 0x14 + 64) = poolv;
            if (poolv && drange_ok((const void*)poolv, (size_t)NEW_ELEM_SIZE)) {
                static const DWORD TABS_OLD[6] = { 0x1278, 0x1D4C, 0x2820, 0x3126, 0x3C78, NEW_GOODS_A };
                for (int k = 0; k < 6; k++) {
                    memcpy(buf + 0x1B0 + 0xC0 + 0x14 + 64 + 4 + k * 0x40,
                           (const BYTE*)poolv + TABS_OLD[k], 0x40);
                    n3 = 6 * 0x40;
                }
            }
        }
        SIZE_T tot = n1 + n2 + 0x14 + 64 + 4 + n3;
        DWORD h = 2166136261u;
        for (SIZE_T i = 0; i < tot; i++) { h ^= buf[i]; h *= 16777619u; }
        if (it == 0 || h != last_hash) {
            last_hash = h;
            CreateDirectoryA("logs", NULL);
            FILE* f = fopen("logs\\region.txt", (it == 0) ? "w" : "a");
            if (f) {
                DWORD gl274 = *(DWORD*)(buf + 0x1B0 + 0xC0 + 0x10);
                fprintf(f, "\n=== region it=%d tick=%lu hash=%08X ===\n", it,
                        GetTickCount(), h);
                fprintf(f, "globals: %08X %08X %08X %08X %08X  @[569274]: ",
                        *(DWORD*)(buf + 0x1B0 + 0xC0), *(DWORD*)(buf + 0x1B0 + 0xC0 + 4),
                        *(DWORD*)(buf + 0x1B0 + 0xC0 + 8), *(DWORD*)(buf + 0x1B0 + 0xC0 + 0xC),
                        *(DWORD*)(buf + 0x1B0 + 0xC0 + 0x10));
                for (int k = 0; k < 64; k++) fprintf(f, "%02X ", buf[0x1B0 + 0xC0 + 0x14 + k]);
                fprintf(f, "\nBD6C0: ");
                for (SIZE_T i = 0; i < n1; i++) fprintf(f, "%02X ", buf[i]);
                fprintf(f, "\nC5100: ");
                for (SIZE_T i = 0; i < n2; i++) fprintf(f, "%02X ", buf[0x1B0 + i]);
                fprintf(f, "\n");
                write_actor_snap(f, gl274, 2);
                fclose(f);
            }
        }
        Sleep(4000);
    }
    return 0;
}

static DWORD WINAPI dump_modules(void*)
{
    CreateDirectoryA("logs", NULL);
    FILE* f = fopen("logs\\modules_etapc.txt", "w");
    if (!f) return 0;
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, GetCurrentProcessId());
    if (snap != INVALID_HANDLE_VALUE) {
        MODULEENTRY32 me;
        me.dwSize = sizeof(me);
        if (Module32First(snap, &me)) {
            do {
                fprintf(f, "%-16s base=%08X size=%08X path=%s\n",
                        me.szModule, (DWORD)me.modBaseAddr, me.modBaseSize, me.szExePath);
            } while (Module32Next(snap, &me));
        }
        CloseHandle(snap);
    }
    fclose(f);
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE hInst, DWORD reason, LPVOID)
{
    (void)hInst;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hInst);
        CreateDirectoryA("logs", NULL);
        FILE* f = fopen("logs\\crash.txt", "w");
        if (f) fclose(f);
        AddVectoredExceptionHandler(1, crash_logger);
        etapc_log("[%s] loaded, PID=%lu\n", DLL_NAME, GetCurrentProcessId());

        /* tryb czysty: ETAPC_NOPATCH=1, plik NOPATCH w CWD albo obok DLL */
        int nopatch = 0;
        {
            char nv[8] = "";
            if (GetEnvironmentVariableA("ETAPC_NOPATCH", nv, sizeof(nv)) > 0 && nv[0] == '1')
                nopatch = 1;
            if (!nopatch && GetFileAttributesA("NOPATCH") != INVALID_FILE_ATTRIBUTES)
                nopatch = 1;
            if (!nopatch) {
                char self[MAX_PATH]; char selfdir[MAX_PATH]; char marker[MAX_PATH];
                DWORD ln = GetModuleFileNameA(hInst, self, MAX_PATH);
                if (ln > 0 && ln < MAX_PATH) {
                    strcpy_s(selfdir, self);
                    char* s = strrchr(selfdir, '\\');
                    if (s) *s = '\0';
                    snprintf(marker, sizeof(marker), "%s\\NOPATCH", selfdir);
                    if (GetFileAttributesA(marker) != INVALID_FILE_ATTRIBUTES)
                        nopatch = 1;
                }
            }
            char cwd[MAX_PATH] = "";
            GetCurrentDirectoryA(MAX_PATH, cwd);
            etapc_log("[%s] cwd=%s nopatch=%d\n", DLL_NAME, cwd, nopatch);
        }
        if (nopatch) {
            etapc_log("[EtapC] tryb CZYSTY (NOPATCH) -> patche POMINIETE\n");
        }
        int ok = nopatch ? 0 : etapc_apply_patches();
        etapc_log("[%s] patches applied: %d/%u ok\n", DLL_NAME, ok, (unsigned)PATCH_COUNT);
        etapc_minhook_init();
        etapc_install_hooks();
        /* DIAGNOSTYKA: zrzut tablic aktora do logs\dump_etapc.txt (WYLACZONE:
           przy blednym wskazniku pool zapetla sie w AV i mrozi gre) */
        CreateThread(NULL, 0, dump_thread, NULL, 0, NULL);
        CreateThread(NULL, 0, dump_modules, NULL, 0, NULL);
        CreateThread(NULL, 0, region_sampler, NULL, 0, NULL);
    }
    return TRUE;
}