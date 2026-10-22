@echo off
cd /d "G:\Games\CnMod 1.2\cnmod_hook"
if exist build rmdir /s /q build
cmake -B build -G "Visual Studio 17 2022" -A Win32
cmake --build build --config Release
