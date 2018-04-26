#!/bin/bash

hexdump -e '"0x%08_ax  |" 1/4 "%08x" "|\n"' $@
