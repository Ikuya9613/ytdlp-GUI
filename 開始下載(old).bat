@echo off
:: 切換編碼至 UTF-8
chcp 65001 > nul
setlocal enabledelayedexpansion

:: 強制切換到此 .bat 檔所在的資料夾
cd /d "%~dp0"

:: --- 設定區 ---
set "TargetFile=待下載清單.txt"

:: 檢查檔案是否存在
if not exist "%TargetFile%" (
    echo ==========================================
    echo  錯誤：找不到檔案 [%TargetFile%]
    echo  請確保檔案位於： %cd%
    echo ==========================================
    pause
    goto :eof
)

echo 偵測到清單，準備開始下載...
echo 檔案路徑: %cd%\%TargetFile%
echo ------------------------------------------

:: 使用 for 迴圈讀取檔案
for /f "usebackq delims=" %%a in ("%TargetFile%") do (
    set "line=%%a"
    
    :: 智慧檢查：只處理以 http 開頭的行 (無視時間戳記與分隔線)
    echo !line! | findstr /i "^http" >nul
    if !errorlevel! equ 0 (
        echo 正在處理網址: !line!
        
        :: 執行 yt-dlp
        yt-dlp -x --audio-format m4a --embed-metadata --embed-thumbnail -P ".\downloads" -o "%(title)s.%(ext)s" "!line!"
        
        echo ------------------------------------------
    )
)

echo.
echo 所有有效連結已處理完畢！
pause