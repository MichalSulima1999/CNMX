#pragma once

#ifndef CNMOD_MEMORY_H
#define CNMOD_MEMORY_H

#include <windows.h>
#include <cstdint>
#include <vector>
#include <string>

namespace CNMod {

// ============================================================================
// Memory Utilities
// ============================================================================

// Read memory with error checking
template<typename T>
bool ReadMemory(uintptr_t address, T& out) {
    if (!address) return false;
    __try {
        out = *reinterpret_cast<T*>(address);
        return true;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

template<typename T>
bool WriteMemory(uintptr_t address, const T& value) {
    if (!address) return false;
    DWORD old_protect;
    if (!VirtualProtect(reinterpret_cast<void*>(address), sizeof(T), PAGE_EXECUTE_READWRITE, nullptr)) {
        return false;
    }
    __try {
        *reinterpret_cast<T*>(address) = value;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        VirtualProtect(reinterpret_cast<void*>(address), sizeof(T), PAGE_READWRITE, nullptr);
        return false;
    }
    return true;
}

// Read byte array
std::vector<uint8_t> ReadBytes(uintptr_t address, size_t size) {
    std::vector<uint8_t> buffer(size);
    if (ReadMemory(address, buffer.data(), size)) {
        return buffer;
    }
    return {};
}

bool ReadMemory(uintptr_t address, void* buffer, size_t size) {
    if (!address || !buffer || size == 0) return false;
    __try {
        memcpy(buffer, reinterpret_cast<void*>(address), size);
        return true;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

bool WriteMemory(uintptr_t address, const void* buffer, size_t size) {
    if (!address || !buffer || size == 0) return false;
    DWORD old_protect;
    if (!VirtualProtect(reinterpret_cast<void*>(address), size, PAGE_EXECUTE_READWRITE, nullptr)) {
        return false;
    }
    __try {
        memcpy(reinterpret_cast<void*>(address), buffer, size);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        VirtualProtect(reinterpret_cast<void*>(address), size, PAGE_READWRITE, nullptr);
        return false;
    }
    return true;
}

// ============================================================================
// Hook Utilities
// ============================================================================

// Write a JMP rel32 instruction at address
// Returns true on success
bool WriteJmpHook(uintptr_t addr, uintptr_t target, size_t instruction_size = 5) {
    if (instruction_size < 5) return false; // Need at least 5 bytes for JMP rel32
    
    DWORD old_protect;
    if (!VirtualProtect(reinterpret_cast<void*>(addr), instruction_size, PAGE_EXECUTE_READWRITE, nullptr)) {
        return false;
    }
    
    // Calculate relative offset
    // JMP rel32 = E9 XX XX XX XX
    // rel32 = target - (addr + 5)
    intptr_t rel32 = static_cast<intptr_t>(reinterpret_cast<uintptr_t>(target) - (addr + 5));
    
    BYTE jmp_instruction[5] = { 0xE9 };
    *reinterpret_cast<int32_t*>(jmp_instruction + 1) = static_cast<int32_t>(rel32);
    
    // Fill remaining bytes with NOP
    std::vector<BYTE> instruction(instruction_size, 0x90); // NOP
    memcpy(instruction.data(), jmp_instruction, 5);
    
    if (!WriteMemory(addr, instruction.data(), instruction_size)) {
        return false;
    }
    
    FlushInstructionCache(GetCurrentProcess(), reinterpret_cast<void*>(addr), instruction_size);
    return true;
}

// Read original bytes before hooking
std::vector<uint8_t> ReadOriginalBytes(uintptr_t addr, size_t size) {
    std::vector<uint8_t> buffer(size);
    if (ReadMemory(addr, buffer.data(), size)) {
        return buffer;
    }
    return {};
}

// Restore original bytes
bool RestoreOriginalBytes(uintptr_t addr, const std::vector<uint8_t>& original) {
    if (original.empty()) return false;
    return WriteMemory(addr, original.data(), original.size());
}

// ============================================================================
// Signature Scanning
// ============================================================================

// Find pattern in memory
// Pattern format: "48 8B 05 ?? ?? ?? ?? 48 85 C0"
// ?? = wildcard
uintptr_t FindPattern(uintptr_t start, size_t size, const char* pattern) {
    // Parse pattern
    std::vector<int> pattern_bytes;
    const char* p = pattern;
    while (*p) {
        while (*p == ' ') ++p;
        if (*p == '?' && *(p+1) == '?') {
            pattern_bytes.push_back(-1);
            p += 2;
        } else {
            char hex[3] = { p[0], p[1], 0 };
            pattern_bytes.push_back(strtol(hex, nullptr, 16));
            p += 2;
        }
        while (*p == ' ') ++p;
    }
    
    // Read memory region
    std::vector<uint8_t> memory(size);
    if (!ReadMemory(start, memory.data(), size)) {
        return 0;
    }
    
    // Search
    for (size_t i = 0; i + pattern_bytes.size() <= size; ++i) {
        bool match = true;
        for (size_t j = 0; j < pattern_bytes.size(); ++j) {
            if (pattern_bytes[j] != -1 && memory[i + j] != pattern_bytes[j]) {
                match = false;
                break;
            }
        }
        if (match) {
            return start + i;
        }
    }
    return 0;
}

// ============================================================================
// Trampoline Helper
// ============================================================================

// Create a trampoline for hooking
// Returns address of trampoline (caller must free with VirtualFree)
void* CreateTrampoline(uintptr_t target, const void* hook, size_t original_size) {
    // Allocate executable memory
    void* trampoline = VirtualAlloc(nullptr, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!trampoline) return nullptr;
    
    BYTE* ptr = static_cast<BYTE*>(trampoline);
    
    // Copy original instructions
    // (In practice, you'd need a disassembler to copy complete instructions)
    // For now, just JMP to hook
    *ptr++ = 0xE9; // JMP rel32
    int32_t rel = static_cast<int32_t>(reinterpret_cast<uintptr_t>(hook) - (reinterpret_cast<uintptr_t>(trampoline) + 5));
    *reinterpret_cast<int32_t*>(ptr) = static_cast<int32_t>(reinterpret_cast<uintptr_t>(hook) - (reinterpret_cast<uintptr_t>(trampoline) + 5));
    ptr += 4;
    
    // JMP back to after original code
    *ptr++ = 0xE9;
    int32_t rel_back = static_cast<int32_t>(
        (reinterpret_cast<uintptr_t>(target) + 5) - 
        (reinterpret_cast<uintptr_t>(trampoline) + 5 + 5)
    );
    *reinterpret_cast<int32_t*>(ptr) = rel_back;
    
    FlushInstructionCache(GetCurrentProcess(), trampoline, ptr - static_cast<BYTE*>(trampoline));
    
    return trampoline;
}

// ============================================================================
// Module Helpers
// ============================================================================

uintptr_t GetModuleBase(const char* module_name = nullptr) {
    return reinterpret_cast<uintptr_t>(GetModuleHandleA(module_name));
}

uintptr_t GetProcAddressSafe(const char* module, const char* proc) {
    HMODULE hMod = GetModuleHandleA(module);
    if (!hMod) return 0;
    return reinterpret_cast<uintptr_t>(GetProcAddress(hMod, proc));
}

} // namespace CNMod

#endif // CNMOD_MEMORY_H