@REM install QGIS custom launcher 
@echo on
echo "Starting postinstall qgis-isl.bat"

set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%

@REM  backup native QGIS bat files and shortcuts

move /Y "%OSGEO4W_ROOT%\bin\qgis-ltr.bat" "%OSGEO4W_ROOT%\bin\qgis-ltr-natif.bat"

move /Y "%AppData%\Microsoft\Windows\Start Menu\Programs\QGIS3.lnk" "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links\
move /Y "%OSGEO4W_STARTMENU%\*" "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links\

@REM  delete of backup link (may remain from previous install)
del "%OSGEO4W_ROOT%\apps\qgis-custom\qgis-ltr-backup\QGIS ISL (LTR).lnk"


@rem copy launcher and make a shortcut in start menu
move /Y "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-isl.bat.template" "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat"

nircmd shortcut "%OSGEO4W_ROOT%\bin\nircmd.exe" "%OSGEO4W_STARTMENU%" "QGIS ISL (LTR)" "exec hide ~q%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat~q" "%OSGEO4W_ROOT%\apps\qgis-ltr\icons\qgis.ico" 

@REM file associations

textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg"
nircmd elevate "%WINDIR%\regedit" /s "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg"

echo "End of qgis-isl postinstall"

@echo off
exit /b 0
.lnk