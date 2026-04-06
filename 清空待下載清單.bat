@echo off
setlocal
chcp 65001 > nul

set "SaveFile=待下載清單.txt"

:: --- 新增：二次確認清空功能 ---
echo ==========================================
echo  注意：您即將清空 %SaveFile% 的所有內容！
echo ==========================================
set /p "Confirm=確定要清空嗎？(輸入 Y 確定，按其他鍵取消): "

if /i "%Confirm%"=="Y" (
    :: 使用空內容覆蓋檔案以達成清空目的
    type build-in > "%SaveFile%" 2>nul || echo. > "%SaveFile%"
    cls
    echo 檔案已成功清空！
    timeout /t 1 > nul
) else (
    echo 已取消清空操作。
    timeout /t 1 > nul
)

:: --- (原有的功能可以接在下方，或者直接結束) ---
goto :eof