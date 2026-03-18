@echo off
echo Suppression des anciens builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Construction du StreamDeck.exe...
pyinstaller --onefile --windowed --name "StreamDeck" ^
  --add-data "src;src" ^
  --hidden-import customtkinter ^
  --hidden-import pyautogui ^
  --hidden-import pyautogui._pyautogui_win ^
  --hidden-import pynput ^
  --hidden-import pynput.keyboard ^
  --hidden-import pynput._win32 ^
  --hidden-import win32gui ^
  --hidden-import win32process ^
  --hidden-import psutil ^
  --hidden-import serial.tools.list_ports ^
  --collect-all customtkinter ^
  --collect-all pynput ^
  deck.py
echo.
echo Termine ! Le .exe est dans le dossier dist/
