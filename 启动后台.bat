@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   正在启动拓达昇官网内容后台...
echo   启动后会自动打开浏览器，请勿关闭本窗口
echo.
python admin\server.py
echo.
echo   后台已退出。按任意键关闭窗口...
pause >nul
