:; f="$1"; shift; exec bash "$(dirname "$0")/$f" "$@" #
@echo off
REM Polyglot wrapper adapted from superpowers 5.1.0 (MIT License)
REM Original: https://github.com/obra/superpowers/blob/main/hooks/run-hook.cmd
REM Copyright (c) Anthropic + superpowers contributors
REM CFP-475 / ADR-038 Amendment 3 §결정 11 (codeforge polyglot pattern)
REM
REM Cross-platform polyglot hook wrapper.
REM   Windows: cmd.exe runs the batch body below (finds Git-Bash and calls it).
REM   Unix:    line 1 execs bash on the target script and never reads the batch.
REM
REM This file MUST be CRLF (.gitattributes pins *.cmd text eol=crlf). cmd.exe
REM mis-parses LF-only batch files -- byte drift makes it echo these comment
REM lines as commands (spurious stderr). The Unix side execs on line 1 before
REM any later line is parsed, so CRLF is harmless there. Do not convert to LF.
REM
REM Hook scripts use extensionless names (e.g. "session-start", not ".sh") so Claude
REM Code's Windows auto-detect -- which prepends "bash" to any .sh command -- won't interfere.
REM
REM Usage: run-hook.cmd <script-name> [args...]
setlocal
set "HOOK_DIR=%~dp0"

if "%~1"=="" (
    echo run-hook.cmd: missing script name 1>&2
    exit /b 1
)

REM Try Git for Windows bash in standard locations
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM Try bash on PATH (e.g. user-installed Git Bash, MSYS2, Cygwin)
where bash >nul 2>nul
if %ERRORLEVEL% equ 0 (
    bash "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM No bash found - exit silently rather than error
exit /b 0
