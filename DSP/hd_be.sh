#!/bin/bash

hexdump -e '"0x%08_ax  |" 4/1 "%02x" "|\n"' $@
