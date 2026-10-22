#!/usr/bin/env python3
"""
CNMod Hook Injector
Wstrzykuje kod do CN.PLMOD.exe używając ctypes i CreateRemoteThread
"""
import ctypes
import ctypes.wintypes
import subprocess
import time
import sys
import os

# Windows API constants
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_EXECUTE_READWRITE = 0x40
CREATE_SUSPENDED = 0x00000004

# Windows API functions
kernel32 = ctypes.windll.kernel32

# ============================================================================
# Metoda 1: prosty injection przez CreateRemoteThread + LoadLibraryA
# Wymaga DLL pliku - użyj metody 2 jeśli nie masz DLL
# ============================================================================

def inject_dll_simple(pid: int, dll_path: str) -> bool:
    """
    Prosty injection DLL przez CreateRemoteThread.
    Uwaga:.dll_path musi być bezwzględną ścieżką.
    """
    dll_path = os.path.abspath(dll_path)
    dll_path_bytes = dll_path.encode('utf-8') + b'\x00'
    
    # Otwórz proces
    hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not hProcess:
        print(f"Nie można otworzyć procesu {pid}: {ctypes.GetLastError()}")
        return False
    
    # Alokuj pamięć na ścieżkę DLL
    remotePath = kernel32.VirtualAllocEx(
        hProcess, None, len(dll_path_bytes),
        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE
    )
    if not remotePath:
        print(f"Nie można zaalokować pamięci: {ctypes.GetLastError()}")
        kernel32.CloseHandle(hProcess)
        return False
    
    # Napisz ścieżkę DLL do pamięci zdalnej
    written = ctypes.c_size_t(0)
    kernel32.WriteProcessMemory(
        hProcess, remotePath, dll_path_bytes,
        len(dll_path_bytes), ctypes.byref(written)
    )
    
    # Znajdź LoadLibraryA
    hKernel32 = kernel32.GetModuleHandleA(b"kernel32.dll")
    loadLibraryAddr = kernel32.GetProcAddress(hKernel32, b"LoadLibraryA")
    
    # Utwórz zdalny wątek
    threadId = ctypes.c_ulong(0)
    hThread = kernel32.CreateRemoteThread(
        hProcess, None, 0, loadLibraryAddr,
        remotePath, 0, ctypes.byref(threadId)
    )
    
    if hThread:
        print(f"Thread utworzony: TID={threadId.value}")
        kernel32.WaitForSingleObject(hThread, 5000)
        kernel32.CloseHandle(hThread)
    
    # Zwolnij pamięć
    kernel32.VirtualFreeEx(hProcess, remotePath, 0, 0x8000)  # MEM_RELEASE
    kernel32.CloseHandle(hProcess)
    
    return True


# ============================================================================
# Metoda 2: Shellcode injection (bez DLL)
# Wstrzykuje kod x86 który wyświetla MessageBox
# ============================================================================

def inject_shellcode_test(pid: int) -> bool:
    """
    Wstrzykuje testowy shellcode (MessageBox) do procesu.
    Kod x86 (32-bit):
    """
    # Shellcode 32-bit: MessageBoxA(0, "Hook dziala!", "CNMod", 0)
    # Uwaga: należy dostosować do 32-bit jeśli gra jest 32-bit
    shellcode = bytes([
        # push 0                    ; uType = MB_OK
        0x6A, 0x00,
        # push "CNMod"              ; lpCaption (hardcoded address placeholder)
        0x68, 0x00, 0x00, 0x00, 0x00,  # placeholder - needs fix
        # push "Hook dziala!"       ; lpText
        0x68, 0x00, 0x00, 0x00, 0x00,  # placeholder - needs fix
        # push 0                    ; hWnd = NULL
        0x6A, 0x00,
        # call MessageBoxA          ; call rel32
        0xE8, 0x00, 0x00, 0x00, 0x00,  # placeholder
        # ret
        0xC3,
    ])
    
    # Na razie - zbyt skomplikowane na placeholder addresses
    # Lepiej użyć CreateRemoteThread z funkcją w procesie
    
    print("Metoda shellcode wymaga przygotowania kodów z prawidłowymi adresami.")
    print("Przejście do metody 3...")
    return False


# ============================================================================
# Metoda 3: Uruchom grę z suspends i stwórz RemoteThread
# Najprostsza - nie wymaga DLL ani shellcode
# ============================================================================

def launch_and_inject(dll_path: str = None) -> bool:
    """
    Uruchamia grę w stanie suspended i wstrzykuje DLL.
    """
    exe_path = r"G:\Games\CnMod 1.2\CN.PLMOD.exe"
    
    # Uruchom proces w stanie suspended
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_SHOWNORMAL
    
    process = subprocess.Popen(
        [exe_path],
        cwd=os.path.dirname(exe_path),
        creationflags=subprocess.CREATE_SUSPENDED
    )
    
    print(f"Proces uruchomiony: PID={process.pid}")
    
    if dll_path and os.path.exists(dll_path):
        inject_dll_simple(process.pid, dll_path)
    else:
        # Wznów proces bez wstrzykiwania
        # Windows nie ma wznów bezpośrednio, ale ResumeThread z kernel32
        kernel32 = ctypes.windll.kernel32
        
        # Pobierz handle procesu
        PROCESS_ALL_ACCESS = 0x1F0FFF
        hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, process.pid)
        
        # Nie ma bezpośredniego ResumeThread dla procesu
        # Trzeba użyć NtContinue lub innego mechanizmu
        # Na razie po prostu czekaj na zakończenie procesu
        print("DLL nie znaleziony - czekanie na zakończenie procesu...")
        process.wait()
    
    return True


def inject_dll_simple(pid: int, dll_path: str) -> bool:
    """
    Prosty injection DLL do procesu.
    """
    dll_path = os.path.abspath(dll_path)
    dll_path_bytes = dll_path.encode('utf-8') + b'\x00'
    
    hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not hProcess:
        print(f"Nie można otworzyć procesu {pid}: {ctypes.GetLastError()}")
        return False
    
    # Alokuj pamięć na ścieżkę DLL
    remotePath = kernel32.VirtualAllocEx(
        hProcess, None, len(dll_path_bytes),
        MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    if not remotePath:
        print(f"Nie można zaalokować pamięci: {ctypes.GetLastError()}")
        kernel32.CloseHandle(hProcess)
        return False
    
    # Napisz ścieżkę DLL do pamięci zdalnej
    written = ctypes.c_size_t(0)
    kernel32.WriteProcessMemory(
        hProcess, remotePath, dll_path_bytes,
        len(dll_path_bytes), ctypes.byref(written)
    )
    
    # Znajdź LoadLibraryA
    kernel32_module = kernel32.GetModuleHandleA(b"kernel32.dll")
    loadLibraryAddr = kernel32.GetProcAddress(kernel32_module, b"LoadLibraryA")
    
    # Utwórz zdalny wątek
    threadId = ctypes.c_ulong(0)
    hThread = kernel32.CreateRemoteThread(
        hProcess, None, 0, loadLibraryAddr,
        remotePath, 0, ctypes.byref(threadId)
    )
    
    if hThread:
        kernel32.WaitForSingleObject(hThread, 5000)
        print(f"DDL wstrzyknął: {dll_path}")
        kernel32.CloseHandle(hThread)
    
    kernel32.VirtualFreeEx(hProcess, remotePath, 0, 0x8000)  # MEM_RELEASE
    kernel32.CloseHandle(hProcess)
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("CNMod Hook DLL Injector")
    print("=" * 60)
    
    dll_path = r"G:\Games\CnMod 1.2\cnmod_hook.dll"
    
    if os.path.exists(dll_path):
        print(f"DLL znaleziony: {dll_path}")
        # TODO: Znajdź uruchomioną grę i wstrzyknij
        print("Szukanie uruchomionej gry...")
    else:
        print(f"DLL nie znaleziony: {dll_path}")
        print("Najpierw zbuduj DLL za pomocą Visual Studio")
    
    print("\nGotowe!")
