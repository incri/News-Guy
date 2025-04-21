@echo off
cd /d "%~dp0"
call env\Scripts\activate
start cmd /k "uvicorn main:app --reload"
code . 