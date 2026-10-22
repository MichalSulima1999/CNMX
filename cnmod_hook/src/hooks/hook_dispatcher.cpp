// Hook 1: Job Dispatcher (0x46BD2F)
// Przechwytuje wywołanie dispatcher jobów i obsługuje nowe joby >46

#include "cnmod_hook.h"
#include "hooks/hook_dispatcher.h"
#include "registry/job_registry.h"
#include "utils/logging.h"
#include <windows.h>

namespace CNMod {

// Original code at 0x46BD2F:
// MOV EAX, [ESI+0x18]     ; get job ID
// DEC EAX                  ; job - 1
// CMP EAX, 0x2E            ; compare with 46
// JA   0x46BE1B            ; if > 46, jump to default

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
        
        // Call custom handler(unit)
        mov ecx, esi              ; unit pointer in ECX
        call edx                  ; custom handler(unit)
        
        popad
        ret
        
    OriginalDefault:
        popad
        jmp CNMod::ORIG_DISPATCHER_DEFAULT
        
    OriginalDispatcher:
        popad
        // Original code continues after our hook
        jmp CNMod::HOOK_DISPATCHER_ADDR + 5
    }
}

bool InstallHook1_Dispatcher() {
    constexpr uintptr_t addr = CNMod::HOOK_DISPATCHER_ADDR; // 0x46BD2F
    constexpr size_t hook_size = 5;  // JMP rel32
    
    DWORD old_protect;
    if (!VirtualProtect((void*)addr, hook_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        LOG_ERROR("VirtualProtect failed for dispatcher hook at 0x%p", (void*)addr);
        return false;
    }
    
    // Save original bytes (for uninstall)
    static BYTE orig_bytes[5];
    memcpy(orig_bytes, (void*)addr, 5);
    
    // Write JMP rel32 to HookedDispatcher
    uintptr_t target = reinterpret_cast<uintptr_t>(&HookedDispatcher);
    int32_t rel32 = static_cast<int32_t>(target - (addr + 5));
    
    BYTE jmp_instruction[5] = { 0xE9 };
    *reinterpret_cast<int32_t*>(jmp_instruction + 1) = rel32;
    
    memcpy((void*)addr, jmp_instruction, 5);
    FlushInstructionCache(GetCurrentProcess(), (void*)addr, 5);
    
    VirtualProtect((void*)addr, hook_size, old_protect, &old_protect);
    
    LOG_INFO("Hook 1 (Dispatcher) installed at 0x%p -> 0x%p", (void*)addr, reinterpret_cast<void*>(&HookedDispatcher));
    return true;
}

} // namespace CNMod