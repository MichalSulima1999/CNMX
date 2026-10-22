#pragma once

#ifdef CNMOD_HOOK_EXPORTS
#define CNMOD_API __declspec(dllexport)
#else
#define CNMOD_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Inicjalizuje hooki (wywoływane przez DllMain automatycznie)
CNMOD_API bool CNMod_Initialize();

// Zamyka hooki
CNMOD_API void CNMod_Shutdown();

// Rejestruje custom job handler
// jobId: ID zawodu (47-127)
// handler: wskaźnik do funkcji __fastcall void handler(void* unit, int param, void* context)
// context: opcjonalny kontekst przekazywany do handlera
CNMOD_API bool CNMod_RegisterJob(uint32_t jobId, void* handler, void* context);

// Usuwa custom job
CNMOD_API void CNMod_UnregisterJob(uint32_t jobId);

// Zwraca liczbę zarejestrowanych custom jobów
CNMOD_API uint32_t CNMod_GetCustomJobCount();

// Sprawdza czy hooki są zainstalowane
CNMOD_API bool CNMod_IsInitialized();

#ifdef __cplusplus
}
#endif
