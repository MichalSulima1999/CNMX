@echo off
rem Build EtapC.dll (x86) + launcher.exe  dla CN.PLMOD.exe
rem Wymaga: .\.tools\mingw32\bin  (MinGW-W64 i686) oraz .\.tools\minhook-master

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

echo == EtapC (C++) ==
"%TOOL%\g++.exe" -O2 -c "%SRC%\log.cpp"     -o "%OUT%\log.o"
"%TOOL%\g++.exe" -O2 -c "%SRC%\EtapC.cpp"   -o "%OUT%\EtapC.o"  -I"%MH%\include" -I"%SRC%" -I"..\etapa_gen"
if errorlevel 1 (echo BLAD EtapC & exit /b 1)

echo == link DLL ==
"%TOOL%\g++.exe" -shared -o EtapC.dll "%OUT%\EtapC.o" "%OUT%\log.o" ^
  "%OUT%\mh_buffer.o" "%OUT%\mh_hook.o" "%OUT%\mh_trampoline.o" ^
  "%OUT%\mh_hde32.o" "%OUT%\mh_hde64.o" -static -s
if errorlevel 1 (echo BLAD link DLL & exit /b 1)

echo == launcher ==
"%TOOL%\g++.exe" -O2 -o launcher.exe "%SRC%\launcher.cpp" -static -static-libgcc -static-libstdc++ -s
if errorlevel 1 (echo BLAD launcher & exit /b 1)

echo == kopiuj do roota (modlauncher laduje ..\EtapC.dll) ==
copy /y EtapC.dll "..\EtapC.dll" >nul
if errorlevel 1 (echo BLAD kopiowania EtapC.dll do roota & exit /b 1)

echo == OK ==
dir /b EtapC.dll launcher.exe
dir /b "..\EtapC.dll"
endlocal