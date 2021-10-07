# 
PLUGIN_NAME=isl_box

SOURCES= \
    __init__.py \
    isl_box.py \
    isl_box_provider.py \
    algorithm \
    icons \
    metadata.txt

deploy:
	mkdir -p deploy/$(PLUGIN_NAME)
	cp -vfr $(SOURCES) deploy/$(PLUGIN_NAME)/

zip: deploy
	rm -f $(PLUGIN_NAME).zip
	cd deploy; zip -9r $(CURDIR)/$(PLUGIN_NAME).zip $(PLUGIN_NAME)
