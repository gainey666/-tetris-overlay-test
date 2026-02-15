@echo off
echo -----------------------------------------------------------
echo  build_board_processor.bat
echo -----------------------------------------------------------

if exist build (
    echo Removing old build folder ...
    rmdir /s /q build
)
mkdir build
cd build

"C:\Program Files\CMake\bin\cmake.exe" .. ^
    -G "NMake Makefiles" ^
    -DCMAKE_TOOLCHAIN_FILE="g:\dad fucken around\tetris again\vcpkg\scripts\buildsystems\vcpkg.cmake" ^
    -DOpenCV_DIR="g:\dad fucken around\tetris again\vcpkg\installed\x64-windows\share\opencv4" ^
    -DCMAKE_VERBOSE_MAKEFILE=ON ^
    -DCMAKE_BUILD_TYPE=Release

echo.
echo ====================  NMake output  ======================
nmake

echo.
echo Copying *.pyd to the Python agents folder ...
copy /Y board_processor_cpp*.pyd "..\..\src\agents\"

echo.
echo ====================  BUILD FINISHED  =====================
