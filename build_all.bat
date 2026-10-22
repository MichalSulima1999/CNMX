@echo off
rem ============================================================================
rem  build_all.bat -- buduje oba komponenty moda i kopiuje je do katalogu gry
rem
rem  Wymaga: .tools\mingw32\bin (MinGW-W64 i686) + .tools\minhook-master
rem  UWAGA: gra musi byc zamknieta (pliki DLL sa zablokowane przez proces).
rem ============================================================================
setlocal
cd /d "%~dp0"

echo.
echo ============ EtapC.dll (patch danych w pamieci) ============
call etapc\build.bat
if errorlevel 1 (
  echo BLAD: build EtapC
  exit /b 1
)

echo.
echo ============ cnmod_hook.dll (hooki behawioralne) ============
call cnmod_hook\build.bat
if errorlevel 1 (
  echo BLAD: build cnmod_hook
  exit /b 1
)

echo.
echo ============ WYNIK ============
dir /b EtapC.dll cnmod_hook.dll 2>nul
for %%F in (EtapC.dll cnmod_hook.dll) do (
  if exist "%%F" (
    for %%A in ("%%F") do echo   %%F  %%~zA B  %%~tA
  ) else (
    echo   BRAK: %%F
  )
)
echo.
echo Gotowe. Uruchom: modlauncher.exe
endlocal
