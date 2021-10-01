SOURCES = __init__.py \
          photo2shapeplugin.py \
          photoimportertask.py \
		  backends/backendbase.py \
		  backends/exifpybackend.py \
		  backends/gdalbackend.py \
          gui/photo2shapedialog.py \
          gui/aboutdialog.py

FORMS = ui/photo2shapedialogbase.ui \
        ui/aboutdialogbase.ui

TRANSLATIONS = i18n/photo2shape_uk.ts \
               i18n/photo2shape_fr.ts
