// Hook 2: Job Assignment (0x43242C)
// Przypisuje job z house_type do unit+0x18

#include "cnmod_hook.h"
#include "hooks/hook_job_assign.h"
#include "registry/job_registry.h"
#include "utils/logging.h"
#include <windows.h>

namespace CNMod {

__declspec(naked) void HookedJobAssign() {
    __asm {
        pushad
        
        // ECX = building, param_1 = unit_id, param_2 = type
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
        jmp CNMod::HOOK_JOB_ASSIGN_ADDR
    }
}

bool InstallHook2_JobAssign() {
    LOG_INFO("Hook 2 (JobAssign) - installing trampoline at 0x43242C");
    // For now, just log - full implementation needs trampoline
    return true;
}

} // namespace CNMod