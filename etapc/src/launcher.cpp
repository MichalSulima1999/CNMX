// launcher.cpp - startuje CN.PLMOD.exe (suspended), wstrzykuje EtapC.dll
// i wznawia glowny watek. Bez zmian dyskowych w exe (rollback = usun DLL).
//
// Uzycie: launcher.exe [sciezka-do-exe] [sciezka-do-dll]
// Domyślnie: CN.PLMOD.exe obok launcher.exe, EtapC.dll obok launcher.exe.
// CWD gry = katalog exe.

#define __USE_MINGW_ANSI_STDIO 1
#include <windows.h>
#include <cstdio>
#include <cstdarg>

static const char* DEFAULT_EXE = "CN.PLMOD.exe";
static const char* DLL_NAME = "EtapC.dll";

static FILE* g_log = nullptr;

static void log(const char* fmt, ...)
{
    char buf[1024];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    fputs(buf, stdout);
    fflush(stdout);
    if (g_log) {
        fputs(buf, g_log);
        fflush(g_log);
    }
}

static bool inject_dll(HANDLE proc, const char* dllFullPathA)
{
    // jako sciezke w procesie bedziemy chcieli posluzyc sie LoadLibraryA
    size_t len = strlen(dllFullPathA) + 1;
    void* remote = VirtualAllocEx(proc, NULL, len, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!remote) {
        log("VirtualAllocEx failed: %lu\n", GetLastError());
        return false;
    }
    SIZE_T written = 0;
    if (!WriteProcessMemory(proc, remote, dllFullPathA, len, &written) || written != len) {
        log("WriteProcessMemory failed: %lu\n", GetLastError());
        VirtualFreeEx(proc, remote, 0, MEM_RELEASE);
        return false;
    }
    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    FARPROC loadLib = GetProcAddress(k32, "LoadLibraryA");
    if (!loadLib) {
        log("GetProcAddress(LoadLibraryA) failed: %lu\n", GetLastError());
        VirtualFreeEx(proc, remote, 0, MEM_RELEASE);
        return false;
    }
    HANDLE thread = CreateRemoteThread(proc, NULL, 0, (LPTHREAD_START_ROUTINE)loadLib, remote, 0, NULL);
    if (!thread) {
        log("CreateRemoteThread failed: %lu\n", GetLastError());
        VirtualFreeEx(proc, remote, 0, MEM_RELEASE);
        return false;
    }
    WaitForSingleObject(thread, 5000);
    DWORD exitCode = 0;
    GetExitCodeThread(thread, &exitCode);
    CloseHandle(thread);
    VirtualFreeEx(proc, remote, 0, MEM_RELEASE);
    if (exitCode == 0) {
        log("LoadLibraryA w procesie zwrocil NULL (modul sie nie zaladowal)\n");
        return false;
    }
    log("DLL wstrzykniety, handle = %p\n", (void*)(uintptr_t)exitCode);
    return true;
}

int main(int argc, char** argv)
{
    char launcherDir[MAX_PATH] = "";
    {
        HMODULE h = GetModuleHandleA(NULL);
        GetModuleFileNameA(h, launcherDir, MAX_PATH);
        char* slash = strrchr(launcherDir, '\\');
        if (slash) *slash = '\0';
    }

    const char* exeArg = (argc > 1 && argv[1][0]) ? argv[1] : DEFAULT_EXE;
    char exePath[MAX_PATH * 2];
    if (strchr(exeArg, '\\') || strchr(exeArg, '/')) {
        GetFullPathNameA(exeArg, MAX_PATH * 2, exePath, NULL);
    } else {
        snprintf(exePath, sizeof(exePath), "%s\\%s", launcherDir, exeArg);
    }

    // CWD gry = katalog exe
    char gameDir[MAX_PATH * 2];
    {
        snprintf(gameDir, sizeof(gameDir), "%s", exePath);
        char* ls = strrchr(gameDir, '\\');
        if (ls) *ls = '\0';
    }

    char dllPath[MAX_PATH * 2];
    if (argc > 2 && argv[2][0]) {
        GetFullPathNameA(argv[2], MAX_PATH * 2, dllPath, NULL);
    } else {
        snprintf(dllPath, sizeof(dllPath), "%s\\%s", launcherDir, DLL_NAME);
    }

    // log
    {
        char logPath[MAX_PATH * 2];
        snprintf(logPath, sizeof(logPath), "%s\\logs\\launcher.log", gameDir);
        g_log = fopen(logPath, "a");
    }

    log("launcher: katalog=%s\n", launcherDir);
    log("launcher: exe=%s\n", exePath);
    log("launcher: dll=%s\n", dllPath);
    log("launcher: cwd=%s\n", gameDir);

    char cmdLine[MAX_PATH * 2];
    snprintf(cmdLine, sizeof(cmdLine), "\"%s\"", exePath);

    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);

    BOOL ok = CreateProcessA(NULL, cmdLine, NULL, NULL, FALSE,
                             CREATE_SUSPENDED, NULL, gameDir, &si, &pi);
    if (!ok) {
        log("CreateProcessA failed: %lu\n", GetLastError());
        if (g_log) fclose(g_log);
        return 1;
    }
    log("proces utworzony (suspended): PID=%lu\n", pi.dwProcessId);

    if (!inject_dll(pi.hProcess, dllPath)) {
        log("UWAGA: brak wstrzykniecia, uruchamiam gre bez overlayu\n");
    }

    // Opcjonalna druga DLL: cnmod_hook.dll (diagnostyka/hooki) obok launchera
    {
        char dll2Path[MAX_PATH * 2];
        snprintf(dll2Path, sizeof(dll2Path), "%s\\cnmod_hook.dll", launcherDir);
        if (GetFileAttributesA(dll2Path) != INVALID_FILE_ATTRIBUTES) {
            if (inject_dll(pi.hProcess, dll2Path))
                log("cnmod_hook.dll wstrzykniety\n");
            else
                log("UWAGA: cnmod_hook.dll NIE wstrzykniety\n");
        }
    }

    ResumeThread(pi.hThread);
    log("glowny watek wznowiony\n");

    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 0;
    GetExitCodeProcess(pi.hProcess, &code);
    log("gra zakonczona, kod = %lu\n", code);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    if (g_log) fclose(g_log);
    return 0;
}