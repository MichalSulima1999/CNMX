// Hook 4: Stock Update (0x44B910)
// tribe_house, good_id, qty, player

#include "cnmod_hook.h"
#include "hooks/hook_stock.h"
#include "utils/logging.h"
#include <windows.h>

namespace CNMod {

__declspec(naked) void HookedStock() {
    __asm {
        pushad
        
        // Stack: [ESP+0x24] = tribe_house, [ESP+0x28] = good_id
        //        [ESP+0x2C] = qty, [ESP+0x30] = player
        
        mov edx, g_custom_stock_handler
        test edx, edx
        jz OriginalStock
        
        mov eax, [esp + 0x30]  ; player
        push eax
        mov eax, [esp + 0x2C]  ; qty
        push eax
        mov eax, [esp + 0x28]  ; good_id
        push eax
        mov eax, [esp + 0x24]  ; tribe_house
        push eax
        mov ecx, esi           ; tribe_house
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

bool InstallHook4_Stock() {
    constexpr uintptr_t addr = CNMod::HOOK_STOCK_ADDR; // 0x44B910
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

} // namespace CNMod