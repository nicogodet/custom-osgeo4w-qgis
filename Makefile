#
PLUGINDIR=/mnt/l/Qgis/PLUGINS

create:
	@echo
	@echo "-----------------------------------"
	@echo "Create OSGeo4W archive."
	@echo "-----------------------------------"
	@scripts/make.sh

deploy: create
	@echo
	@echo "-----------------------------------"
	@echo "Deploy OSGeo4W archive."
	@echo "-----------------------------------"
	@scripts/deploy.sh

pclean:
	@echo
	@echo "-----------------------------------"
	@echo "Clean plugin directory."
	@echo "-----------------------------------"
	find $(PLUGINDIR)/ -iname "__pycache__" -prune -exec rm -Rf {} \;
	find $(PLUGINDIR)/ -iname ".git" -prune -exec rm -Rf {} \;
