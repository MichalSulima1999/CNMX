#pragma once
#include <windows.h>

/* logi (zdefiniowane w osobnej jednostce; plywanie do stdout + plik) */
#ifdef __cplusplus
extern "C" {
#endif
void etapc_log(const char* fmt, ...);
#ifdef __cplusplus
}
#endif

/*
 * Tabela runtime-pathy dla CN.PLMOD.exe (ImageBase 0x400000, x86).
 *
 * Konwencja: adres podajemy jako RVA od ImageBase (VA = 0x400000 + RVA),
 * dzieki czemu dziala niezaleznie od ASLR (gra to legacy PE bez ASLR,
 * ImageBase jest stale, ale zapis rva-owy jest odporny).
 */

typedef struct {
    DWORD rva;          /* RVA od ImageBase */
    BYTE  off;          /* offset w instrukcji do nadpisania */
    BYTE  size;         /* liczba bajtow do nadpisania */
    BYTE  bytes[8];     /* nowe bajty (male koncowka) */
    const char* desc;   /* opis */
} Patch;

/* Nowe limity Etap C:
 *  houses: 55 -> 64   (akceptowane 1..63)
 *  goods : 66 -> 97   (akceptowane 1..96)
 *  Mieszcza sie w pojedynczym bajcie (<=127) wiec imm8 cmp wystarcza. */
#define NEW_HOUSE_MAX   0x40   /* 64 */
#define NEW_GOOD_MAX    0x61   /* 97 */

/*
 * Rozszerzenie rekordu plemienia (wariant "pojazdy -> ogon"), bez przesuwania
 * displacementow pol rekordu:
 *  - tablica flag domow +0x515C ma 55 B; brakuje 9 B do 64 -> 0x515C..0x519B,
 *  - zwalniamy je, przenoszac 8-bajtowa tablice pojazdow (0x5193) na ogon rekordu,
 *  - rekord rosnie o 8 B: 0x1AE08 -> 0x1AE10 (42 rekordy: 0x468EA0),
 *  - WSZYSTKIE pola od +0x519C w gore zostaja na swoich offsetach (zero
 *    patchy displacementow).
 */
#define TRIBE_REC_SIZE_OLD  0x1AE08
#define TRIBE_REC_SIZE_NEW  0x1AE10   /* +8 B na przeniesione pojazdy */
#define TRIBE_ARR_SIZE_NEW  (42 * TRIBE_REC_SIZE_NEW)   /* 0x468EA0 */
#define VEH_DISP_OLD        0x5193
#define VEH_DISP_NEW        TRIBE_REC_SIZE_OLD          /* 0x1AE08 */

/* size_t uzyty w mallocach (pierwotnie 55*0x624=0x151BC, 66*0xD0=0x35A0) */
static inline DWORD houses_malloc_size(void) { return (DWORD)(NEW_HOUSE_MAX * 0x624u); }
static inline DWORD goods_malloc_size(void)  { return (DWORD)(NEW_GOOD_MAX  * 0xD0u); }

static const Patch PATCHES[] = {
    /* 1. petla ladowania domow: inc edx; cmp edx,0x37; jb  -> limit 0x40 */
    { 0x000A003, 2, 1, { NEW_HOUSE_MAX }, "loop houses < 64" },
    /* 2. validator NC2Logic: cmp eax,0x37; jge err -> house id < 64 */
    { 0x0014289, 2, 1, { NEW_HOUSE_MAX }, "validator house < 64" },
    /* 3. validator NC2Logic: cmp edi,0x42; jge err -> good id < 97 */
    { 0x0014292, 2, 1, { NEW_GOOD_MAX },  "validator good < 97" },
    /* 4. malloc tablicy domow: mov esi, imm32 */
    { 0x001534E, 1, 4, { 0, 0, 0, 0 },    "malloc houses table" },
    /* 5. malloc tablicy surowcow: mov esi, imm32 */
    { 0x001595E, 1, 4, { 0, 0, 0, 0 },    "malloc goods table" },

    /* ==== Rozszerzenie slotow domow (ID 55..63) ====================== *
     * Wariant "pojazdy -> ogon": nie przesuwamy pol rekordu; przenosimy *
     * 8-bajtowa tablice pojazdow i powiekszamy rekord o 8 B.            *
     * Wygenerowane/zweryfikowane przez .ai/scripts/gen_tribe_patches.py */

    /* limity 0x37 -> 0x40 */
    { 0x0009EA1, 2, 1, { NEW_HOUSE_MAX }, "flag copy loop < 64" },
    { 0x00142F4, 2, 1, { NEW_HOUSE_MAX }, "flag write guard < 64" },
    { 0x001542C, 2, 1, { NEW_HOUSE_MAX }, "houses.ini loader < 64" },
    { 0x00158D5, 3, 1, { NEW_HOUSE_MAX }, "tribe iterator 1 < 64" },
    { 0x0015923, 2, 1, { NEW_HOUSE_MAX }, "tribe iterator 2 < 64" },
    { 0x0015368, 3, 4, { NEW_HOUSE_MAX, 0, 0, 0 }, "ctor: 64 records" },

    /* tablica pojazdow 0x5193 -> ogon rekordu 0x1AE08 */
    { 0x0009EA8, 3, 4, { 0x08, 0xAE, 0x01, 0x00 }, "vehicles read -> tail" },
    { 0x00142BB, 3, 4, { 0x08, 0xAE, 0x01, 0x00 }, "vehicles write -> tail" },

    /* rozmiar rekordu plemienia 0x1AE08 -> 0x1AE10 */
    { 0x0009E00, 3, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe size (mov)" },
    { 0x000A032, 3, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe size (strided)" },
    { 0x000AF4A, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe size (advance)" },
    { 0x0013F56, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe size (imul)" },
    /* koniec tablicy plemion 0x468D50 -> 0x468EA0 */
    { 0x000AF51, 2, 4, { 0xA0, 0x8E, 0x46, 0x00 }, "tribe array end (cmp)" },
    { 0x0013EAB, 1, 4, { 0xA0, 0x8E, 0x46, 0x00 }, "tribe array malloc" },

    /* 24x imul ...,0x1AE08 w kodzie menu/logiki (obszerne zero patchy disp) */
    { 0x02D80A, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x02D84F, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x02D894, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x02D8D9, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x02D91E, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x02D940, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x02DB3A, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x03E8C7, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04A147, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04A216, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04A365, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04A5AF, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04A9AF, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04AA9E, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04ABED, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04AE56, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04B282, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04B313, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x04CB19, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x0A5356, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x0A57E7, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x0A5AF6, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x0AC6FE, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
    { 0x0C7821, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe stride imul" },
};

#define PATCH_COUNT (sizeof(PATCHES) / sizeof(PATCHES[0]))

/* aplikuje patche do bie�cego procesu; zwraca liczbe udanych */
static int etapc_apply_patches(void)
{
    /* ETAPC_NOPATCH=1 (env) lub plik NOPATCH w CWD -> tryb czysty (diagnostyka) */
    char nv[8] = "";
    if ((GetEnvironmentVariableA("ETAPC_NOPATCH", nv, sizeof(nv)) > 0 && nv[0] == '1')
        || GetFileAttributesA("NOPATCH") != INVALID_FILE_ATTRIBUTES) {
        etapc_log("[EtapC] tryb CZYSTY (NOPATCH) -> patche POMINIETE\n");
        return 0;
    }
    int ok = 0;
    HMODULE mod = GetModuleHandleW(L"CN.PLMOD.exe");
    if (!mod)
        mod = GetModuleHandleW(NULL);
    BYTE* base = (BYTE*)mod;
    DWORD prev = 0;

    for (size_t i = 0; i < PATCH_COUNT; ++i) {
        Patch p = PATCHES[i];
        BYTE* addr = base + p.rva + p.off;
        /* dla mallocow uzupelnij wartosc runtime */
        if (i == 3) {
            DWORD v = houses_malloc_size();
            p.bytes[0] = v & 0xFF; p.bytes[1] = (v >> 8) & 0xFF;
            p.bytes[2] = (v >> 16) & 0xFF; p.bytes[3] = (v >> 24) & 0xFF;
        } else if (i == 4) {
            DWORD v = goods_malloc_size();
            p.bytes[0] = v & 0xFF; p.bytes[1] = (v >> 8) & 0xFF;
            p.bytes[2] = (v >> 16) & 0xFF; p.bytes[3] = (v >> 24) & 0xFF;
        }
        if (!VirtualProtect(addr, p.size, PAGE_EXECUTE_READWRITE, &prev)) {
            etapc_log("patch %u (rva %08X) VirtualProtect FAILED\n", (unsigned)i, p.rva);
            continue;
        }
        memcpy(addr, p.bytes, p.size);
        VirtualProtect(addr, p.size, prev, &prev);
        etapc_log("patch %u ok: %s (rva %08X off %u len %u)\n",
                  (unsigned)i, p.desc, p.rva, p.off, p.size);
        ++ok;
    }
    return ok;
}