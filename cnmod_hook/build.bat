@echo off
rem Build cnmod_hook.dll (x86) - Faza 1: diagnostyczne hooki (MinHook)
rem Wymaga: .\.tools\mingw32\bin (MinGW-W64 i686) oraz .\.tools\minhook-master
rem Analogiczne do etapc\build.bat.

setlocal
cd /d "%~dp0"

set TOOL=..\.tools\mingw32\bin
set MH=..\.tools\minhook-master
set SRC=src
set OUT=build
set PATH=%TOOL%;%PATH%

if not exist "%TOOL%\gcc.exe" (echo BRAK: %TOOL%\gcc.exe & exit /b 1)
if not exist "%MH%\include\MinHook.h" (echo BRAK: MinHook & exit /b 1)
if not exist "%OUT%" mkdir "%OUT%"

echo == MinHook (C) ==
"%TOOL%\gcc.exe" -O2 -c "%MH%\src\buffer.c"     -o "%OUT%\mh_buffer.o"     -I"%MH%\src"
"%TOOL%\gcc.exe" -O2 -c "%MH%\src\hook.c"       -o "%OUT%\mh_hook.o"       -I"%MH%\src"
"%TOOL%\gcc.exe" -O2 -c "%MH%\src\trampoline.c" -o "%OUT%\mh_trampoline.o" -I"%MH%\src"
"%TOOL%\gcc.exe" -O2 -c "%MH%\src\hde\hde32.c"  -o "%OUT%\mh_hde32.o"      -I"%MH%\src"
"%TOOL%\gcc.exe" -O2 -c "%MH%\src\hde\hde64.c"  -o "%OUT%\mh_hde64.o"      -I"%MH%\src"
if errorlevel 1 (echo BLAD MinHook & exit /b 1)

echo == cnmod_hook (C++) ==
"%TOOL%\g++.exe" -O2 -c "%SRC%\main.cpp" -o "%OUT%\main.o" -I"%MH%\include" -Iinclude -DCNMOD_HOOK_EXPORTS
if errorlevel 1 (echo BLAD cnmod_hook & exit /b 1)

echo == link DLL ==
"%TOOL%\g++.exe" -shared -o cnmod_hook.dll "%OUT%\main.o" ^
  "%OUT%\mh_buffer.o" "%OUT%\mh_hook.o" "%OUT%\mh_trampoline.o" ^
  "%OUT%\mh_hde32.o" "%OUT%\mh_hde64.o" -static -s
if errorlevel 1 (echo BLAD link DLL & exit /b 1)

echo == kopiuj do roota (modlauncher wstrzykuje ..\cnmod_hook.dll) ==
copy /y cnmod_hook.dll "..\cnmod_hook.dll" >nul
if errorlevel 1 (echo BLAD kopiowania do roota & exit /b 1)

echo == OK ==
dir /b cnmod_hook.dll
dir /b "..\cnmod_hook.dll"
endlocal
