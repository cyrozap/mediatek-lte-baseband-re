#!/bin/bash

adb shell su echo echo  6 \\\> /sys/kernel/ccci/debug
adb shell su echo echo smem \\\> /sys/kernel/ccci/mdsys1/dump
adb shell dmesg | grep sush | grep ccci
