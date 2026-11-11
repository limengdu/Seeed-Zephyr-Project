# XIAO nRF54LM20B

## Factory firmware layout

The USB-C port connects directly to the nRF54LM20B. The factory MCUboot chain
uses the following internal-flash partitions:

| Region | Start | Size |
| --- | --- | --- |
| MCUboot | `0x000000` | 24 KiB |
| Application slot 0 | `0x006000` | 1784 KiB |
| Firmware loader in slot 1 | `0x1C4000` | 116 KiB |
| Storage | `0x1E1000` | 124 KiB |

Build the application for `xiao_nrf54lm20b/nrf54lm20b/cpuapp` with
`CONFIG_MCUBOOT_BOOTLOADER_MODE_FIRMWARE_UPDATER=y`, pure Ed25519 signing, and
the workspace MCUboot development key `bootloader/mcuboot/root-ed25519.pem`.
The image header occupies `0x800` bytes. Upload uses
`build/zephyr/zephyr.signed.confirmed.bin` and preserves the factory loader.

## Entering the USB loader

The running application uses USB id `2886:8013`; the factory loader uses
`2886:0013` and identifies itself as `CDC ACM serial backend`.

For the first upload from the factory Thread Co-Processor application, hold the
user button (Button 0, P0.09) while pressing RESET, then release the button.
Holding Button 0 while connecting USB also enters the loader. Once the loader
appears, run Upload again.

The repository blinky example handles subsequent uploads automatically. The CLI
opens its serial port at 9600 baud and then 1200 baud, with DTR low. The example
checks the USB line settings every 50 ms, records
`BOOT_MODE_TYPE_BOOTLOADER` through `zephyr,boot-mode`, and reboots. MCUboot then
starts the factory loader. This path requires the line-control, reboot, and
retained boot-mode options in the example's `prj.conf`.

## Image transfer

The CLI sends the signed image through the existing Python serial environment
using the loader's SMP image-upload protocol. Transfer verification uses a
32-byte SHA-256 digest of the complete upload file. The image's pure Ed25519
signature and SHA-512 image hash remain part of the signed image.

Nordic `nrfutil mcu-manager` 0.12.3 puts the image's 64-byte SHA-512 hash into
the upload request. The factory loader limits this transfer field to 32 bytes
and returns `MGMT_ERR_EINVAL`; protocol version 2 reports image-group error 24
(`INVALID_HASH`). The built-in uploader supplies the supported transfer digest
and advances according to the byte offset acknowledged by the board.

## Console and LEDs

The application console is USB CDC ACM at 115200 baud. A successful blinky
upload identifies as `XIAO nRF54LM20B` and prints the Zephyr boot banner followed
by alternating `LED state: OFF` and `LED state: ON` lines. The blue LED is `led0`
(GPIO1 pin 23, active low); red and green are `led1` and `led2`.

Create a fresh example project with plugin 0.5.7 or later to include the USB
identity and automatic loader-entry handler.
