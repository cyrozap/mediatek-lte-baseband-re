#!/bin/bash
set -e

adb wait-for-device
adb reboot bootloader

fastboot boot ./bootimg/boot_new.img

adb wait-for-device
sleep 30
adb shell "su -c setenforce permissive"
adb shell getenforce
