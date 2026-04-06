@echo off
setlocal
:: 設定編碼為 UTF-8 (避免中文亂碼)
chcp 65001 > nul

:: --- 設定：您想儲存內容的檔案位置 ---
:: 預設為與 bat 同目錄下的 "待下載清單.txt"
set "SaveFile=待下載清單.txt"

:: --- 步驟 1：偵測 (讀取) 目前剪貼簿內容 ---
:: 使用 PowerShell 讀取剪貼簿並存入暫存變數
for /f "usebackq delims=" %%I in (`powershell -command "Get-Clipboard"`) do (
    set "ClipContent=%%I"
)

:: 檢查剪貼簿是否為空
if "%ClipContent%"=="" (
    echo 剪貼簿是空的，或內容非純文字。
    pause
    goto :eof
)

:: --- 步驟 2：直接透過 PowerShell 讀取並追加到檔案 ---
:: 這種寫法最安全，完全不會觸發 Batch 的符號錯誤
powershell -Command "$clip = Get-Clipboard; if ($clip) { Add-Content -Path '%SaveFile%' -Value ($clip) } else { throw 'Clipboard is empty' }" >nul 2>&1

:: --- 步驟 3：完成提示 ---
cls
echo ==========================================
echo  成功！已將剪貼簿內容追加到: %SaveFile%
echo ==========================================
echo  內容預覽：
echo  %ClipContent%
echo ==========================================
:: 設定延遲 0.3 秒後自動關閉，不需要手動按
timeout /t 0.3 > nul