# Run Makefile in generator subdir
.PRECIOUS: $(CONFIGURED_BUILD_SOURCE)
$(CONFIGURED_BUILD_SOURCE):
	$(MAKE) -C $(TEMPLATES_DIR)/$(SOURCE_PROJECT)