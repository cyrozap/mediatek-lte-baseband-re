all: hello-aarch64 mode-switch write-sequence

hello-aarch64 mode-switch write-sequence:
	$(MAKE) -C $@

clean:
	$(MAKE) -C hello-aarch64 clean
	$(MAKE) -C mode-switch clean
	$(MAKE) -C write-sequence clean

.PHONY: all clean hello-aarch64 mode-switch write-sequence
