#
PACKAGE_DIR = "/mnt/l/Qgis/DEPLOY/depot"
REF_PLUGINS_PATH = "/mnt/l/Qgis/PLUGINS"

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
	find $(REF_PLUGINS_PATH)/ -iname "__pycache__" -prune -exec rm -Rf {} \;
	find $(REF_PLUGINS_PATH)/ -iname ".git" -prune -exec rm -Rf {} \;
