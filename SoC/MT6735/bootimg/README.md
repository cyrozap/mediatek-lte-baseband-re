# boot.img

## Building

1. Build the kernel using the instructions in the `../kernel` directory.
2. Extract the `boot.img` from the `boot` partition of your android
   device and place it in the `./dump` directory.
3. Run `./build.sh` in this `bootimg` directory.
4. Boot your device from the newly-generated `boot_new.img` file.
