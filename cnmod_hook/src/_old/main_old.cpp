// CNMod Hook System - Main Entry Point
// DLL injected into CN.PLMOD.exe

#include "cnmod_hook.h"
#include "hooks/hook_dispatcher.h"
#include "hooks/hook_job_assign.h"
#include "hooks/hook_production.h"
#include "hooks/hook_stock.h"
#include "registry/job_registry.h"
#include "registry/production_registry.h"
#include "registry/good_registry.h"
#include "registry/ui_registry.h"
#include "ipc/pipe_server.h"
#include "utils/logging.h"
#include "utils/memory.h"
#include "utils/ini_parser.h"

#include <windows.h>
#include <thread>
#include <atomic>

namespace CNMod {

// ============================================================================
// Global State
// ============================================================================

std::atomic<bool> g_hooks_installed{false};
std::atomic<bool> g_hot_reload_requested{false};
std::atomic<bool> g_shutdown_requested{false};

// Original function pointers
HookDispatcherFn g_orig_dispatcher = nullptr;
HookJobAssignFn g_orig_job_assign = nullptr;
HookProductionFn g_orig_production = nullptr;
HookStockFn g_orig_stock = nullptr;

// Custom handlers (set by registry)
HookDispatcherFn g_custom_dispatcher_handler = nullptr;
HookJobAssignFn g_custom_job_assign_handler = nullptr;
HookProductionFn g_custom_production_handler = nullptr;
HookStockFn g_custom_stock_handler = nullptr;

// IPC Server thread
std::thread g_ipc_thread;
std::atomic<bool> g_ipc_running{false};

// ============================================================================
// Hook Implementations
// ============================================================================

// Hook 1: Job Dispatcher (0x46BD2F)
__declspec(naked) void HookedDispatcher() {
    __asm {
        // Save registers
        pushad
        
        // Get job ID from unit (ESI = unit pointer)
        mov eax, [esi + 0x18]     ; job ID
        
        // Check if job >= 46 (0x2E)
        cmp eax, 0x2E
        jb OriginalDispatcher     ; < 46 -> original dispatcher
        
        // Job >= 46: check custom handler
        mov edx, g_custom_dispatcher_handler
        test edx, edx
        jz OriginalDefault
        
        // Call custom handler
        mov ecx, esi              ; unit pointer in ECX
        call edx                  ; custom handler(unit)
        
        popad
        ret
        
    OriginalDefault:
        popad
        jmp CNMod::ORIG_DISPATCHER_DEFAULT
        
    OriginalDispatcher:
        popad
        // Original code: DEC EAX; CMP EAX, 0x2E; JA default; MOVZX...
        // Jump to after our hook
        jmp CNMod::HOOK_DISPATCHER_ADDR + 5
    }
}

// Hook 2: Job Assignment (0x43242C)
// Called before searching house_type workers array
__declspec(naked) void HookedJobAssign() {
    __asm {
        pushad
        
        // ECX = building, [ESP+0x24] = unit_id, [ESP+0x28] = type
        // Save parameters
        mov eax, [esp + 0x24]  ; unit_id
        mov ecx, [esp + 0x28]  ; type
        
        // Check custom handler
        mov edx, g_custom_job_assign_handler
        test edx, edx
        jz OriginalJobAssign
        
        // Call custom handler(building, unit_id, type)
        push ecx              ; type
        push eax              ; unit_id
        mov ecx, esi          ; building (was in ESI)
        call edx
        
        // Result in EAX
        mov [esp + 0x1C], eax ; save return value
        
        popad
        ret
        
    OriginalJobAssign:
        popad
        // Original code continues...
        jmp CNMod::HOOK_JOB_ASSIGN_ADDR
    }
}

// Hook 3: Production Handler (0x46D53A)
// Called from potter handler
__declspec(naked) void HookedProduction() {
    __asm {
        pushad
        
        // ECX = unit
        mov edx, g_custom_production_handler
        test edx, edx
        jz OriginalProduction
        
        mov ecx, esi          ; unit
        call edx
        
        popad
        ret
        
    OriginalProduction:
        popad
        jmp CNMod::HOOK_PRODUCTION_ADDR
    }
}

// Hook 4: Stock Update (0x44B910)
// tribe_house, good_id, qty, player
__declspec(naked) void HookedStock() {
    __asm {
        pushad
        
        // Stack: [ESP+0x24] = tribe_house, [ESP+0x28] = good_id
        //        [ESP+0x2C] = qty, [ESP+0x30] = player
        
        mov edx, g_custom_stock_handler
        test edx, edx
        jz OriginalStock
        
        // Prepare args
        mov eax, [esp + 0x30]  ; player
        push eax
        mov eax, [esp + 0x2C]  ; qty
        push eax
        mov eax, [esp + 0x28]  ; good_id
        push eax
        mov eax, [esp + 0x24]  ; tribe_house
        push eax
        mov ecx, esi           ; tribe_house (usually in ESI)
        call edx
        add esp, 16
        
        mov [esp + 0x1C], eax  ; save return
        
        popad
        ret
        
    OriginalStock:
        popad
        jmp CNMod::HOOK_STOCK_ADDR
    }
}

// ============================================================================
// Hook Installation
// ============================================================================

bool InstallHooks() {
    if (g_hooks_installed.load()) {
        LOG_WARN("Hooks already installed");
        return true;
    }
    
    LOG_INFO("Installing hooks...");
    
    bool success = true;
    
    // Hook 1: Dispatcher (0x46BD2F) - 5 byte JMP
    success &= InstallHook1_Dispatcher();
    
    // Hook 2: Job Assignment (0x43242C) - inline hook
    success &= InstallHook2_JobAssign();
    
    // Hook 3: Production (0x46D53A) - JMP hook
    success &= InstallHook3_Production();
    
    // Hook 4: Stock (0x44B910) - JMP hook
    success &= InstallHook4_Stock();
    
    if (success) {
        g_hooks_installed.store(true);
        LOG_INFO("All hooks installed successfully");
    } else {
        LOG_ERROR("Failed to install some hooks");
        UninstallHooks();
    }
    
    return success;
}

bool UninstallHooks() {
    if (!g_hooks_installed.load()) {
        return true;
    }
    
    LOG_INFO("Uninstalling hooks...");
    
    // Restore original bytes for each hook
    // ... implementation in hook files
    
    g_hooks_installed.store(false);
    LOG_INFO("Hooks uninstalled");
    return true;
}

// ============================================================================
// Hook 1: Dispatcher (0x46BD2F) - 5 byte JMP
// ============================================================================

bool InstallHook1_Dispatcher() {
    constexpr uintptr_t addr = CNMod::HOOK_DISPATCHER_ADDR;
    constexpr size_t hook_size = 5;  // JMP rel32
    
    // Original bytes: 8B 46 18 48 3D (MOV EAX,[ESI+0x18]; DEC EAX; CMP EAX,0x2E)
    // We'll JMP to our HookedDispatcher
    
    DWORD old_protect;
    if (!VirtualProtect((void*)addr, hook_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        LOG_ERROR("VirtualProtect failed for dispatcher hook");
        return false;
    }
    
    // Save original bytes (for uninstall)
    static BYTE orig_bytes[5];
    memcpy(orig_bytes, (void*)addr, 5);
    
    // Write JMP rel32
    // JMP rel32 = E9 XX XX XX XX
    // rel32 = target - (addr + 5)
    uintptr_t target = reinterpret_cast<uintptr_t>(&HookedDispatcher);
    int32_t rel32 = static_cast<int32_t>(target - (addr + 5));
    
    BYTE jmp_instruction[5] = { 0xE9 };
    *reinterpret_cast<int32_t*>(jmp_instruction + 1) = rel32;
    
    memcpy((void*)addr, jmp_instruction, 5);
    
    // Flush instruction cache
    FlushInstructionCache(GetCurrentProcess(), (void*)addr, 5);
    
    VirtualProtect((void*)addr, hook_size, old_protect, &old_protect);
    
    LOG_INFO("Hook 1 (Dispatcher) installed at 0x%p -> 0x%p", (void*)addr, reinterpret_cast<void*>(&HookedDispatcher));
    return true;
}

bool InstallHook2_JobAssign() {
    // Inline hook at 0x43242C - save registers, call custom handler
    // This is more complex - use a trampoline
    LOG_INFO("Hook 2 (JobAssign) - TODO: implement trampoline");
    return true;  // TODO
}

bool InstallHook3_Production() {
    constexpr uintptr_t addr = CNMod::HOOK_PRODUCTION_ADDR;
    constexpr size_t hook_size = 5;
    
    DWORD old_protect;
    if (!VirtualProtect((void*)addr, hook_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        LOG_ERROR("VirtualProtect failed for production hook");
        return false;
    }
    
    static BYTE orig_bytes[5];
    memcpy(orig_bytes, (void*)addr, 5);
    
    uintptr_t target = reinterpret_cast<uintptr_t>(&HookedProduction);
    int32_t rel32 = static_cast<int32_t>(target - (addr + 5));
    
    BYTE jmp_instruction[5] = { 0xE9 };
    *reinterpret_cast<int32_t*>(jmp_instruction + 1) = rel32;
    
    memcpy((void*)addr, jmp_instruction, 5);
    FlushInstructionCache(GetCurrentProcess(), (void*)addr, 5);
    VirtualProtect((void*)addr, hook_size, old_protect, &old_protect);
    
    LOG_INFO("Hook 3 (Production) installed at 0x%p", (void*)addr);
    return true;
}

bool InstallHook4_Stock() {
    constexpr uintptr_t addr = CNMod::HOOK_STOCK_ADDR;
    constexpr size_t hook_size = 5;
    
    DWORD old_protect;
    if (!VirtualProtect((void*)addr, hook_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        LOG_ERROR("VirtualProtect failed for stock hook");
        return false;
    }
    
    static BYTE orig_bytes[5];
    memcpy(orig_bytes, (void*)addr, 5);
    
    uintptr_t target = reinterpret_cast<uintptr_t>(&HookedStock);
    int32_t rel32 = static_cast<int32_t>(target - (addr + 5));
    
    BYTE jmp_instruction[5] = { 0xE9 };
    *reinterpret_cast<int32_t*>(jmp_instruction + 1) = rel32;
    
    memcpy((void*)addr, jmp_instruction, 5);
    FlushInstructionCache(GetCurrentProcess(), (void*)addr, 5);
    VirtualProtect((void*)addr, hook_size, old_protect, &old_protect);
    
    LOG_INFO("Hook 4 (Stock) installed at 0x%p", (void*)addr);
    return true;
}

bool UninstallHooks() {
    LOG_INFO("Uninstalling hooks... (TODO: restore original bytes)");
    return true;
}

// ============================================================================
// Custom Handler Registration
// ============================================================================

void SetCustomDispatcherHandler(HookDispatcherFn handler) {
    g_custom_dispatcher_handler = handler;
}

void SetCustomJobAssignHandler(HookJobAssignFn handler) {
    g_custom_job_assign_handler = handler;
}

void SetCustomProductionHandler(HookProductionFn handler) {
    g_custom_production_handler = handler;
}

void SetCustomStockHandler(HookStockFn handler) {
    g_custom_stock_handler = handler;
}

// ============================================================================
// Initialization
// ============================================================================

bool InitializeHookSystem() {
    LOG_INFO("=== CNMod Hook System Initializing ===");
    
    // 1. Initialize registries (load from INI)
    LOG_INFO("Initializing registries...");
    auto& job_reg = JobRegistry::Instance();
    auto& prod_reg = ProductionRegistry::Instance();
    auto& good_reg = GoodRegistry::Instance();
    auto& ui_reg = UIRegistry::Instance();
    
    // Load from INI files
    const char* houses_ini = "CN.PLMOD\\types\\houses.ini";
    const char* goods_ini = "Data\\logic\\goodtypes.ini";
    const char* tribe_ini = "CN.PLMOD\\tribetypes12\\tribetypes.ini";
    
    if (std::filesystem::exists(houses_ini)) {
        JobRegistry::Instance().LoadFromINI(houses_ini);
    }
    if (std::filesystem::exists(goods_ini)) {
        GoodRegistry::Instance().LoadFromINI(goods_ini);
    }
    
    // 2. Install hooks
    if (!InstallHooks()) {
        LOG_ERROR("Failed to install hooks");
        return false;
    }
    
    // 3. Start IPC server
    if (!StartIPCServer()) {
        LOG_ERROR("Failed to start IPC server");
        return false;
    }
    
    LOG_INFO("=== CNMod Hook System Ready ===");
    return true;
}

void ShutdownHookSystem() {
    LOG_INFO("Shutting down hook system...");
    g_shutdown_requested.store(true);
    
    StopIPCServer();
    UninstallHooks();
    
    LOG_INFO("Hook system shutdown complete");
}

// ============================================================================
// Hot Reload
// ============================================================================

void RequestHotReload() {
    g_hot_reload_requested.store(true);
    LOG_INFO("Hot reload requested");
}

void ProcessHotReload() {
    if (!g_hot_reload_requested.load()) return;
    
    LOG_INFO("Processing hot reload...");
    
    // Reload INI files
    JobRegistry::Instance().HotReload();
    ProductionRegistry::Instance().HotReload();
    GoodRegistry::Instance().HotReload();
    UIRegistry::Instance().HotReload();
    
    g_hot_reload_requested.store(false);
    LOG_INFO("Hot reload complete");
}

// ============================================================================
// DLL Entry Point
// ============================================================================

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            DisableThreadLibraryCalls(hModule);
            InitializeHookSystem();
            break;
            
        case DLL_PROCESS_DETACH:
            if (!g_shutdown_requested) {
                ShutdownHookSystem();
            }
            break;
    }
    return TRUE;
}

// Exported functions for external tools
extern "C" __declspec(dllexport) bool CNMod_Initialize() {
    return InitializeHookSystem();
}

extern "C" __declspec(dllexport) void CNMod_Shutdown() {
    ShutdownHookSystem();
}

extern "C" __declspec(dllexport) void CNMod_RequestHotReload() {
    RequestHotReload();
}

extern "C" __declspec(dllexport) bool CNMod_IsReady() {
    return g_hooks_installed.load();
}

} // namespace CNMod