@REM  puts back QGIS native launchers and file associations 

echo "running .bat preremove qgis-isl "

set O4W_ROOT=%OSGEO4W_ROOT%
set OSGEO4W_ROOT=%OSGEO4W_ROOT:\=\\%

set APPNAME=QGIS ISL (LTR)

@REM  deletes .bat et and custom shortcuts
del "%OSGEO4W_ROOT%\bin\data\QGIS\QGIS3\qgis_constrained_settings.yml"
del "%OSGEO4W_ROOT%\bin\data\QGIS\QGIS3\startup.py"
del "%OSGEO4W_ROOT%\bin\qgis-ltr-isl.bat"
del "%OSGEO4W_ROOT%\bin\update-isl.bat"
del "%OSGEO4W_STARTMENU%\%APPNAME%.lnk"
del "%OSGEO4W_STARTMENU%\Mise a jour %APPNAME%.lnk"
del "%OSGEO4W_DESKTOP%\%APPNAME%.lnk"

@REM cleans python compiled files (should be adapted to Python3 cache)
del /s /q "%OSGEO4W_ROOT%\apps\qgis-isl\python\*.pyc"

@REM deletes custom shortcut backup (may remain)
del "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\%APPNAME%.lnk"
del "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\Mise a jour %APPNAME%.lnk"

@REM delete old reg key association
del "%OSGEO4W_ROOT%\apps\qgis-isl\bin\qgis-isl-ltr.reg"

@REM restore native shortcuts
move /Y "%OSGEO4W_ROOT%\bin\qgis-ltr-natif.bat" "%OSGEO4W_ROOT%\bin\qgis-ltr.bat"
move /Y "%OSGEO4W_ROOT%\apps\qgis-isl\qgis-ltr-backup\startmenu_links\*.lnk" "%OSGEO4W_STARTMENU%\"

@REM  replays file associations for qgs / qgz with QGIS native

set OSGEO4W_ROOT=%O4W_ROOT%
textreplace -std -t "%OSGEO4W_ROOT%\apps\qgis-ltr\bin\qgis.reg"
if not exist "%OSGEO4W_ROOT%\apps\qgis\bin\qgis.reg" "%WINDIR%\regedit" /s "%OSGEO4W_ROOT%\apps\qgis-ltr\bin\qgis.reg"
