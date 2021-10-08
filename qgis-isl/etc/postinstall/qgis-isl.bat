@REM install QGIS custom launcher 
@echo on
echo "Starting postinstall qgis-isl.bat"

if not defined OSGEO4W_DESKTOP for /F "tokens=* USEBACKQ" %%F IN (`getspecialfolder Desktop`) do set OSGEO4W_DESKTOP=%%F
@REM Temp overwrite OSGEO4W_DESKTOP_LINKS (https://trac.osgeo.org/osgeo4w/ticket/693)
set OSGEO4W_DESKTOP_LINKS=1

set APPNAME=QGIS ISL (LTR)
for %%i in ("%OSGEO4W_STARTMENU%") do set QGIS_WIN_APP_NAME=%%~ni\%APPNAME%
textreplace -std -t "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" -map "set VSI_CACHE=TRUE" "set VSI_CACHE=FALSE"
call "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" --postinstall

set O4W_ROOT=%OSGEO4W_ROOT%
set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%

@REM  backup native QGIS bat files and shortcuts
move /Y "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" "%OSGEO4W_ROOT%\bin\qgis-ltr-natif.bat"
mkdir "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links"
move /Y "%AppData%\Microsoft\Windows\Start Menu\Programs\QGIS3.lnk" "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links"
move /Y "%OSGEO4W_STARTMENU%\*" "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links"

@REM  delete of backup link (may remain from previous install)
del "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\%APPNAME%.lnk"

@rem copy launcher and make a shortcut in start menu
move /Y "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-isl.bat.template" "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat"
move /Y "%OSGEO4W_ROOT%\apps\qgis-isl\update-isl.bat.template" "%OSGEO4W_ROOT%\bin\update-isl.bat"

echo on

if not %OSGEO4W_MENU_LINKS%==0 if not exist "%OSGEO4W_STARTMENU%" mkdir "%OSGEO4W_STARTMENU%"
if not %OSGEO4W_DESKTOP_LINKS%==0 if not exist "%OSGEO4W_DESKTOP%" mkdir "%OSGEO4W_DESKTOP%"

if not %OSGEO4W_MENU_LINKS%==0 xxmklink "%OSGEO4W_STARTMENU%\%APPNAME%.lnk" "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat" "" "%DOCUMENTS%" "" 1 "%OSGEO4W_ROOT%\apps\qgis-ltr\icons\qgis.ico"
if not %OSGEO4W_MENU_LINKS%==0 xxmklink "%OSGEO4W_STARTMENU%\Mise a jour %APPNAME%.lnk" "%OSGEO4W_ROOT%\bin\bgspawn.exe" "\"%OSGEO4W_ROOT%\bin\update-isl.bat\"" "%DOCUMENTS%" "" 1 "%OSGEO4W_ROOT%\OSGeo4W.ico"
if not %OSGEO4W_DESKTOP_LINKS%==0 xxmklink "%OSGEO4W_DESKTOP%\%APPNAME%.lnk" "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat" "" "%DOCUMENTS%" "" 1 "%OSGEO4W_ROOT%\apps\qgis-ltr\icons\qgis.ico"

textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg"
textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-isl\QGIS\QGISCUSTOMIZATION3.ini"
textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-isl\qgis_global_settings.ini"
textreplace -std -t "%OSGEO4W_ROOT%\bin\update-isl.bat"
set OSGEO4W_ROOT=%O4W_ROOT%

REM Do not register extensions if release is installed
if not exist "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg" "%WINDIR%\regedit" /s "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg"
del /s /q "%OSGEO4W_ROOT%\apps\qgis-ltr\python\*.pyc"

echo "End of qgis-isl.bat postinstall"
exit /b 0
