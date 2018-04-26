#!/bin/bash

hexdump -v -e '1/4 "%d\n"' $@
