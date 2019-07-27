all: hello-aarch64 mode-switch

hello-aarch64 mode-switch:
	$(MAKE) -C $@

clean:
	$(MAKE) -C hello-aarch64 clean
	$(MAKE) -C mode-switch clean

.PHONY: all clean hello-aarch64 mode-switch
