@echo off
rem =========================================================================
rem Compilation script for Windows using MS-MPI (Microsoft MPI) or MinGW
rem =========================================================================

echo Checking for MS-MPI SDK environment variables...

if defined MSMPI_INC (
    echo MS-MPI Include Directory: "%MSMPI_INC%"
) else (
    echo [NOTE] MSMPI_INC not defined in environment. Using default path if available.
    set "MSMPI_INC=C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
)

if defined MSMPI_LIB64 (
    echo MS-MPI Lib Directory: "%MSMPI_LIB64%"
) else (
    set "MSMPI_LIB64=C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64"
)

rem Check if cl.exe (MSVC) is available
where cl.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Compiling with Microsoft Visual C++ (cl.exe)...
    cl.exe /nologo /O2 /I"%MSMPI_INC%" 01_basic_exchange.c /link /LIBPATH:"%MSMPI_LIB64%" msmpi.lib /out:01_basic_exchange.exe
    cl.exe /nologo /O2 /I"%MSMPI_INC%" 02_deadlock_free_exchange.c /link /LIBPATH:"%MSMPI_LIB64%" msmpi.lib /out:02_deadlock_free_exchange.exe
    cl.exe /nologo /O2 /I"%MSMPI_INC%" 03_nonblocking_exchange.c /link /LIBPATH:"%MSMPI_LIB64%" msmpi.lib /out:03_nonblocking_exchange.exe
    cl.exe /nologo /O2 /I"%MSMPI_INC%" 04_array_computation_exchange.c /link /LIBPATH:"%MSMPI_LIB64%" msmpi.lib /out:04_array_computation_exchange.exe
    echo Build complete!
    goto :run_info
)

rem Check if gcc is available
where gcc.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Compiling with MinGW GCC...
    gcc -O3 -I"%MSMPI_INC%" 01_basic_exchange.c -L"%MSMPI_LIB64%" -lmsmpi -o 01_basic_exchange.exe
    gcc -O3 -I"%MSMPI_INC%" 02_deadlock_free_exchange.c -L"%MSMPI_LIB64%" -lmsmpi -o 02_deadlock_free_exchange.exe
    gcc -O3 -I"%MSMPI_INC%" 03_nonblocking_exchange.c -L"%MSMPI_LIB64%" -lmsmpi -o 03_nonblocking_exchange.exe
    gcc -O3 -I"%MSMPI_INC%" 04_array_computation_exchange.c -L"%MSMPI_LIB64%" -lmsmpi -o 04_array_computation_exchange.exe
    echo Build complete!
    goto :run_info
)

echo [ERROR] Neither MSVC (cl.exe) nor GCC found in PATH.
exit /b 1

:run_info
echo.
echo To run locally:
echo   mpiexec -n 2 01_basic_exchange.exe
echo.
echo To run across two networked machines:
echo   mpiexec -hosts 2 System1 1 System2 1 01_basic_exchange.exe
