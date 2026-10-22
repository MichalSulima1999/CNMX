// ============================================================================
// CNMod Hook DLL - DLL do CN.PLMOD.exe (Knights & Merchants type game)
// Obsługuje nowe budynki, surowce i zawody poprzez hooki na kluczowe funkcje
//
// Kompilacja: cl.exe /LD /O2 cnmod_hook.cpp /link /OUT:cnmod_hook.dll
// ============================================================================

#include <windows.h>
#include <cstdint>
#include <cstring>
#include <map>
#include <mutex>
#include "cnmod_hook.h"

// ============================================================================
// Adresy z RE (VA = ImageBase 0x400000 + RVA)
// ============================================================================

// Kluczowe funkcje do hookowania:
#define ADDR_DISPATCHER         0x46BD2F   // FUN_0046BAD7 - dispatcher jobów
#define ADDR_JOB_ASSIGN         0x43242C     // FUN_0043242C - przypisuje job do jednostki
#define ADDR_PRODUCTION         0x473461     // FUN_00473461 - unit tick (production)
#define ADDR_FUN_0042DA65       0x42DA65     // FUN_0042DA65 - bramka produkcji
#define ADDR_FUN_004316F3       0x4316F3     // FUN_004316F3 - bramka budynku (revmap)
#define ADDR_FUN_0044A0D9       0x44A0D9     // FUN_0044A0D9 - ustawia +0x195 dla job goods
#define ADDR_POTTER_HANDLER     0x46D53A     // FUN_0046D53A - potter handler (uniwersalny)

// Globalne tablice (VA)
#define DAT_HOUSE_TYPES         0x5113A0     // house_type records
#define DAT_UNITS               0x510BD8     // unit array
#define DAT_TRIBE_HOUSE         0x510BE0     // tribe house array
#define DAT_BUILDING_INSTANCES  0x568C0C     // building instances

// Strides
#define STRIDE_HOUSE_TYPE       0x624
#define STRIDE_UNIT             0xC58
#define STRIDE_TRIBE_HOUSE      0x54C
#define STRIDE_BUILDING         0x7E0

// Offsety w structures
#define OFF_UNIT_JOB            0x18         // job ID w unit
#define OFF_UNIT_BUILDING_IDX   0xB34        // building index w unit
#define OFF_UNIT_CAN_PRODUCE    0x195        // can_produce[good] w unit
#define OFF_UNIT_PROD_STATUS    0x21C        // job_good_status[good] w unit
#define OFF_BUILDING_HOUSE_TYPE 0x14         // house_type index w building

// ============================================================================
// HookedDispatcher - zastępuje oryginalny dispatcher (0x46BD2F)
// ============================================================================
// Original code:
//   mov eax, [esi+0x18]    ; load job ID
//   dec eax
//   cmp eax, 0x2E          ; compare with 46
//   ja  0x46BE1B           ; if > 46, go to default (no job)
//   ...
//
// Our hook intercepts BEFORE the CMP and handles job IDs >= 46:
__declspec(naked) void HookedDispatcher()
{
    __asm
    {
        // Save registers
        pushad
        pushfd

        // Get job ID from unit (ESI points to unit)
        mov eax, [esi + 0x18]

        // Check if job ID >= 46 (our custom range)
        cmp eax, 46
        jb UseOriginalDispatcher   ; if job < 46, use original dispatcher

        // Job >= 46: check if we have a custom handler
        mov ecx, eax               // job ID -> ECX
        test ecx, ecx
        jz UseOriginalDispatcher   // job ID 0 = invalid

        // Look up custom handler from our map
        // g_customJobHandlers is a std::map<uint32_t, void*>
        // For simplicity, we check if handler exists:
        push eax                   // save job ID
        call GetCustomJobHandler   // return handler address in EAX
        test eax, eax
        jz UseOriginalDispatcher   // no handler found -> original

        // Call custom handler (this = unit, edx = param)
        mov ecx, esi               // this = unit pointer
        call eax                   // call handler(unit)

        popfd
        popad
        jmp DispatcherDone         ; done, don't call original

    UseOriginalDispatcher:
        popfd
        popad
        // Continue with original code: DEC EAX; CMP EAX, 0x2E; ...
        mov eax, [esi + 0x18]
        dec eax
        cmp eax, 0x2E
        jmp short DefaultCase

    DefaultCase:
        jmp ADDR_DEFAULT           // jump to 0x46BE1B

    DispatcherDone:
        popfd
        popad
        ret
    }
}

// ============================================================================
// HookedJobAssign - hook na FUN_0043242C
// Przypisuje job do jednostki na podstawie house_type workers
// ============================================================================
__declspec(naked) void HookedJobAssign()
{
    __asm
    {
        pushad
        pushfd

        // this = building (ECX), param_1 = unit ID (EDX), param_2 = type (EAX)
        mov eax, [esp + 0x24]    // unit_id
        mov ecx, [esp + 0x28]    // type

        // Check if we have custom handler for this job
        mov edx, g_customJobHandlers
        test edx, edx
        jz OriginalJobAssign

        mov eax, [esp + 0x24]    // unit_id
        call ecx                   // call handler(unit_id, job_id, type)

        mov [esp + 0x1C], eax      // save return value
        popfd
        popad
        ret

    OriginalJobAssign:
        popfd
        popad
        jmp ADDR_JOB_ASSIGN       // jmp to 0x43242C
    }
}

// ============================================================================
// HookedProduction - hook na FUN_00473461 (unit tick/production)
// ============================================================================
__declspec(naked) void HookedProduction()
{
    __asm
    {
        pushad
        pushfd

        // this = unit (ECX)
        mov eax, [ecx + 0x18]    // job ID of unit

        // Check if job >= 46
        cmp eax, 46
        jb UseOriginalProduction

        // For custom jobs, call custom production handler
        mov edx, g_customProductionHandler
        test edx, edx
        jz UseOriginalProduction

        mov ecx, ecx             // this = unit
        call edx                 // call handler(unit)

        popfd
        popad
        ret                      // skip original production logic

    UseOriginalProduction:
        popfd
        popad
        jmp ADDR_PRODUCTION      // jump to original 0x473461
    }
}

// ============================================================================
// Global state
// ============================================================================

static bool g_hooksInstalled = false;
static std::map<uint32_t, void*> g_customJobHandlers;
static std::mutex g_jobMutex;

// Function pointer type for custom job handler
typedef void (__fastcall *CustomJobHandlerFn)(void* unit, int param);

// Original dispatcher pointer (points to trampoline)
static void* g_originalDispatcher = nullptr;

// ============================================================================
// Hook installation
// ============================================================================

static bool InstallDispatcherHook()
{
    const uintptr_t addr = ADDR_DISPATCHER;
    constexpr size_t hookSize = 5;  // JMP rel32 = 5 bytes

    DWORD oldProtect;
    if (!VirtualProtect((void*)addr, hookSize, PAGE_EXECUTE_READWRITE, &oldProtect))
        return false;

    // Save original bytes
    static BYTE origBytes[5];
    memcpy(origBytes, (void*)addr, 5);

    // Write JMP rel32 to HookedDispatcher
    uint8_t jmpPatch[5] = { 0xE9 };
    int32_t relOffset = (int32_t)((uintptr_t)&HookedDispatcher - (addr + 5));
    *(int32_t*)(jmpPatch + 1) = relOffset;
    memcpy((void*)addr, jmpPatch, 5);

    FlushInstructionCache(GetCurrentProcess(), (void*)addr, hookSize);
    VirtualProtect((void*)addr, hookSize, oldProtect, &oldProtect);

    return true;
}

bool UninstallHook_Dispatcher()
{
    if (!g_hooksInstalled) return true;

    HANDLE hProcess = GetCurrentProcess();
    uint8_t orig[5] = { 0x8B, 0x46, 0x18, 0x48, 0x3D };
    DWORD oldProtect;
    if (!VirtualProtect((void*)ADDR_DISPATCHER, 5, PAGE_EXECUTE_READWRITE, &oldProtect))
        return FALSE;

    memcpy((void*)ADDR_DISPATCHER, orig, 5);
    FlushInstructionCache(GetCurrentProcess(), (void*)ADDR_DISPATCHER, 5);
    VirtualProtect((void*)ADDR_DISPATCHER, 5, oldProtect, &oldProtect);

    g_hooksInstalled = false;
    return TRUE;
}

// ============================================================================
// Exported API for mod tools
// ============================================================================

extern "C" __declspec(dllexport) bool CNMod_RegisterJob(uint32_t jobId, void* handler)
{
    if (jobId < MAX_JOBS_ORIGINAL || jobId >= MAX_JOBS_EXTENDED)
        return false;

    std::lock_guard<std::mutex> lock(g_mutex);
    g_customJobHandlers[jobId] = handler;
    return true;
}

extern "C" __declspec(dllexport) void CNMod_UnregisterJob(uint32_t jobId)
{
    if (jobId >= MAX_JOBS_EXTENDED) return;
    std::lock_guard<std::mutex> lock(g_mutex);
    g_customJobHandlers.erase(jobId);
}

extern "C" __declspec(dllexport) uint32_t CNMod_GetCustomJobCount()
{
    std::lock_guard<std::mutex> lock(g_mutex);
    return (uint32_t)g_customJobHandlers.size();
}

extern "C" __declspec(dllexport) bool CNMod_IsInitialized()
{
    return g_hooksInstalled;
}

// ============================================================================
// DLL Entry Point
// ============================================================================

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved)
{
    switch (reason)
    {
        case DLL_PROCESS_ATTACH:
            DisableThreadLibraryCalls(hModule);

            // Auto-install hooks when DLL is injected
            if (!g_hooksInstalled)
            {
                if (!InstallHook_Dispatcher())
                    return FALSE;

                g_hooksInstalled = true;
            }
            break;

        case DLL_PROCESS_DETACH:
            if (g_hooksInstalled)
                UninstallHook_Dispatcher();
            break;
    }
    return TRUE;
}