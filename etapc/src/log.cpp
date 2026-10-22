// log.cpp - minimal logger dla EtapC DLL
#define __USE_MINGW_ANSI_STDIO 1
#include <windows.h>
#include <cstdio>
#include <cstdarg>

static FILE* etapc_open_log(void)
{
    CreateDirectoryA("logs", NULL);
    FILE* f = fopen("logs\\etapc.log", "a");
    if (!f) {
        char tmp[MAX_PATH], path[MAX_PATH];
        if (GetTempPathA(MAX_PATH, tmp)) {
            snprintf(path, sizeof(path), "%s\\etapc.log", tmp);
            f = fopen(path, "a");
        }
    }
    return f;
}

extern "C" void etapc_log(const char* fmt, ...)
{
    char buf[1024];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    FILE* f = etapc_open_log();
    if (f) {
        fputs(buf, f);
        fclose(f);
    }
    OutputDebugStringA(buf);
}