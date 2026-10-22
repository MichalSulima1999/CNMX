// Hook 3: Production Handler (0x46D53A)
// Called from potter handler for production logic

#include "cnmod_hook.h"
#include "hooks/hook_production.h"
#include "utils/logging.h"
#include <windows.h>

namespace CNMod {

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

bool InstallHook3_Production() {
    constexpr uintptr_t addr = CNMod::HOOK_PRODUCTION_ADDR; // 0x46D53A
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

} // namespace CNMod