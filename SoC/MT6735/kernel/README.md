# kernel

## Building

1. Run `./build.sh` to download the toolchain and kernel sources, patch
   the kernel sources, generate and patch the kernel config, and build
   the kernel.
   -  If you've already applied patches, use the `./rebuild.sh` script instead.
2. Your new kernel will be placed in
   `./android_kernel_mediatek_mt6735/arch/arm/boot/zImage-dtb`.
