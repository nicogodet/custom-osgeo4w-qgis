#
PACKAGE_DIR = "/mnt/l/Qgis/DEPLOY/http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2fv2%2f"
REF_PLUGINS_PATH = "//islsudouest/users/Godet/Qgis/DEPLOY/Plugins"
PLUGINS_PATH = "/mnt/l/Qgis/DEPLOY/Plugins"


create:
	@echo
	@echo "-----------------------------------"
	@echo "Create OSGeo4W archive."
	@echo "-----------------------------------"
	@scripts/make.sh $(REF_PLUGINS_PATH)

deploy: pclean create
	@echo
	@echo "-----------------------------------"
	@echo "Deploy OSGeo4W archive."
	@echo "-----------------------------------"
	@scripts/deploy.sh $(PACKAGE_DIR)

pclean:
	@echo
	@echo "-----------------------------------"
	@echo "Clean plugin directory."
	@echo "-----------------------------------"
	find $(PLUGINS_PATH)/ -iname "__pycache__" -prune -exec rm -Rf {} \;
	find $(PLUGINS_PATH)/ -iname ".git" -prune -exec rm -Rf {} \;
