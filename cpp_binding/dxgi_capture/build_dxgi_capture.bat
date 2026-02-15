@echo off
setlocal ENABLEDELAYEDEXPANSION

set "VSDEV=C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat"
if not exist "%VSDEV%" (
    echo VsDevCmd not found at %VSDEV%
    exit /b 1
)

call "%VSDEV%"

if exist build (
    rmdir /s /q build || exit /b 1
)
mkdir build || exit /b 1
cd build || exit /b 1

"C:\Program Files\CMake\bin\cmake.exe" .. ^
    -G "NMake Makefiles" ^
    -DCMAKE_TOOLCHAIN_FILE="g:\dad fucken around\tetris again\vcpkg\scripts\buildsystems\vcpkg.cmake" ^
    -DOpenCV_DIR="g:\dad fucken around\tetris again\vcpkg\installed\x64-windows\share\opencv4" ^
    -DCMAKE_VERBOSE_MAKEFILE=ON ^
    -DCMAKE_BUILD_TYPE=Release || exit /b 1

nmake || exit /b 1

copy /Y dxgi_capture*.pyd "..\..\src\agents\" || exit /b 1

endlocal
