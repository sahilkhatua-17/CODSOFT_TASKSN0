@echo off
title Rock Paper Scissors - Animated Arena
echo Starting Rock Paper Scissors...
py main.py
if %ERRORLEVEL% NEQ 0 (
    python main.py
)
pause

