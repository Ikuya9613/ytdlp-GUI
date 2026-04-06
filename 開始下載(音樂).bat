@echo off
:: 設定編碼為 UTF-8，避免中文顯示亂碼
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ===================================================
echo     yt-dlp 音訊下載腳本
echo ===================================================
echo.

:: --- 定義共用的 yt-dlp 下載指令 ---
:: 注意：在 bat 檔中，變數 %(title)s 必須寫成 %%(title)s
set "YTDLP_CMD=yt-dlp -x --audio-format m4a --embed-metadata --embed-thumbnail -P ".\downloads" -o "%%(title)s.%%(ext)s" --cookies "cookies.txt""

:: ==========================================
:: [優先級 1] 偵測是否有連結直接拖曳/傳入
:: ==========================================
if not "%~1"=="" (
    :: 簡單判斷拖入的是不是一個純文字檔（比如清單），如果是檔案就當清單讀，否則當單一網址
    if exist "%~1" (
        echo [來源 1 成功] 偵測到拖曳了清單檔案！
        set "TARGET_TYPE=LIST"
        set "TARGET=%~1"
    ) else (
        echo [來源 1 成功] 偵測到直接傳入的連結！
        set "TARGET_TYPE=SINGLE"
        set "TARGET=%~1"
    )
    goto :START_DOWNLOAD
)

:: ==========================================
:: [優先級 2] 偵測剪貼簿是否有連結
:: ==========================================
echo [檢查中] 拖曳來源為空，正在檢查剪貼簿...
:: 透過 PowerShell 讀取剪貼簿，並逐行檢查
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "Get-Clipboard" 2^>nul`) do (
    set "CLIP_TEXT=%%i"
    :: 檢查字串開頭是否為 http (不分大小寫)
    if /I "!CLIP_TEXT:~0,4!"=="http" (
        echo [來源 2 成功] 從剪貼簿抓取到有效連結！
        set "TARGET_TYPE=SINGLE"
        set "TARGET=!CLIP_TEXT!"
        goto :START_DOWNLOAD
    )
)

:: ==========================================
:: [優先級 3] 檢查同目錄下的 "待下載清單.txt"
:: ==========================================
echo [檢查中] 剪貼簿無連結，正在檢查 待下載清單.txt...
if exist "待下載清單.txt" (
    :: 檢查檔案裡面是不是空的，如果有內容就觸發
    for /f "usebackq" %%A in ("待下載清單.txt") do (
        echo [來源 3 成功] 找到 待下載清單.txt 且內有資料！
        set "TARGET_TYPE=LIST"
        set "TARGET=待下載清單.txt"
        goto :START_DOWNLOAD
    )
    echo [提示] 待下載清單.txt 存在，但是是空的。
)

:: ==========================================
:: [全部失敗] 回報無連結
:: ==========================================
echo.
echo [錯誤] 找不到任何可用的下載連結！
echo 請確認符合以下任一操作：
echo   1. 將網址或清單 txt 拖曳到此 bat 檔上
echo   2. 先複製好 YouTube 網址 (存於剪貼簿)
echo   3. 在同目錄建立 "待下載清單.txt" 並貼入網址
echo.
pause
exit /b


:: ==========================================
:: 執行下載區塊 (前面只要成功就會跳躍到這裡)
:: ==========================================
:START_DOWNLOAD
echo.
echo ---------------------------------------------------
if "!TARGET_TYPE!"=="SINGLE" (
    echo 準備下載單一連結：!TARGET!
    %YTDLP_CMD% "!TARGET!"
) else if "!TARGET_TYPE!"=="LIST" (
    echo 準備批次下載清單：!TARGET!
    :: yt-dlp 使用 -a 參數來讀取 txt 檔案內的批次網址
    %YTDLP_CMD% -a "!TARGET!"
)
echo ---------------------------------------------------
echo.
echo 下載任務結束！
pause