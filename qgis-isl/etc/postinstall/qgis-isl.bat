@REM install QGIS custom launcher 
@echo on
echo "Starting postinstall qgis-isl.bat"

set O4W_ROOT=%OSGEO4W_ROOT%
set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%

@REM  backup native QGIS bat files and shortcuts

move /Y "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" "%OSGEO4W_ROOT%\bin\qgis-ltr-natif.bat"

move /Y "%AppData%\Microsoft\Windows\Start Menu\Programs\QGIS3.lnk" "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links\
move /Y "%OSGEO4W_STARTMENU%\*" "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links\

@REM  delete of backup link (may remain from previous install)
del "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\QGIS ISL (LTR).lnk"


@rem copy launcher and make a shortcut in start menu
move /Y "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-isl.bat.template" "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat"

call "%OSGEO4W_ROOT%\bin\o4w_env.bat"

if not defined OSGEO4W_DESKTOP for /F "tokens=* USEBACKQ" %%F IN (`getspecialfolder Desktop`) do set OSGEO4W_DESKTOP=%%F
for /F "tokens=* USEBACKQ" %%F IN (`getspecialfolder Documents`) do set DOCUMENTS=%%F

set APPNAME=QGIS ISL (LTR)
for %%i in ("%OSGEO4W_STARTMENU%") do set QGIS_WIN_APP_NAME=%%~ni\%APPNAME%
call "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat" --postinstall
echo on

if not %OSGEO4W_MENU_LINKS%==0 if not exist "%OSGEO4W_STARTMENU%" mkdir "%OSGEO4W_STARTMENU%"
if not %OSGEO4W_DESKTOP_LINKS%==0 if not exist "%OSGEO4W_DESKTOP%" mkdir "%OSGEO4W_DESKTOP%"

if not %OSGEO4W_MENU_LINKS%==0 xxmklink "%OSGEO4W_STARTMENU%\%APPNAME%.lnk" "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat" "" "%DOCUMENTS%"
if not %OSGEO4W_DESKTOP_LINKS%==0 xxmklink "%OSGEO4W_DESKTOP%\%APPNAME%.lnk" "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat" "" "%DOCUMENTS%"

textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg"
set OSGEO4W_ROOT=%O4W_ROOT%

REM Do not register extensions if release is installed
if not exist "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg" "%WINDIR%\regedit" /s "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg"
del /s /q "%OSGEO4W_ROOT%\apps\qgis-ltr\python\*.pyc"
exit /b 0
