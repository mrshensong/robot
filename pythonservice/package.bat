@echo off
echo remove old file
rd/s/q .\dist
pyinstaller manage.spec
echo copy requirement file
xcopy .\brainstem .\dist\python_service\brainstem\ /e
xcopy .\python_service.bat .\dist\python_service
echo package complete
pause