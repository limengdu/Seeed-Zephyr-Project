/*
 * Shared XIAO board runtime helpers for Grove examples.
 * Keeps USB console startup and 1200-baud bootloader entry aligned with the
 * board baseline examples.
 *
 * Grove 示例共用的 XIAO 板级运行辅助代码。
 * 让 USB 控制台启动和 1200 baud bootloader 入口与板级基础示例保持一致。
 */

#include "xiao_board_runtime.h"

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#if defined(CONFIG_USB_DEVICE_STACK) && !defined(CONFIG_USB_DEVICE_STACK_NEXT)
#include <zephyr/usb/usb_device.h>
#endif

#include <zephyr/drivers/uart.h>
#include <zephyr/sys/reboot.h>

#if defined(CONFIG_RETENTION_BOOT_MODE)
#include <zephyr/retention/bootmode.h>
#endif

#if defined(CONFIG_SOC_SERIES_RA4M1)
#include <bsp_api.h>
#endif

#if defined(CONFIG_SOC_FAMILY_NORDIC_NRF)
#include <hal/nrf_power.h>
#endif

#define XIAO_BOOTLOADER_BAUD_RATE 1200U
#define XIAO_BOOTLOADER_POLL_INTERVAL_MS 50

#if defined(CONFIG_RETENTION_BOOT_MODE) && DT_NODE_HAS_STATUS(DT_NODELABEL(cdc_acm_uart0), okay)
#define XIAO_RUNTIME_CDC_NODE DT_NODELABEL(cdc_acm_uart0)
#define XIAO_RUNTIME_HAS_BOOTLOADER_REQUEST 1
#define XIAO_RUNTIME_HAS_RETENTION_BOOTMODE 1
#elif defined(CONFIG_SOC_SERIES_RA4M1) && DT_NODE_HAS_STATUS(DT_NODELABEL(cdc_acm_uart0), okay)
#define XIAO_RUNTIME_CDC_NODE DT_NODELABEL(cdc_acm_uart0)
#define XIAO_RUNTIME_HAS_BOOTLOADER_REQUEST 1
#define XIAO_RUNTIME_HAS_RA4M1_BOOTMODE 1
#elif defined(CONFIG_SOC_FAMILY_NORDIC_NRF) && DT_NODE_HAS_STATUS(DT_NODELABEL(board_cdc_acm_uart), okay)
#define XIAO_RUNTIME_CDC_NODE DT_NODELABEL(board_cdc_acm_uart)
#define XIAO_RUNTIME_HAS_BOOTLOADER_REQUEST 1
#define XIAO_RUNTIME_HAS_NRF52_BOOTMODE 1
#endif

#if defined(XIAO_RUNTIME_HAS_BOOTLOADER_REQUEST)
static const struct device *const xiao_cdc_uart = DEVICE_DT_GET(XIAO_RUNTIME_CDC_NODE);
#endif

#if defined(XIAO_RUNTIME_HAS_RA4M1_BOOTMODE)
#define RA4M1_BOOTLOADER_MAGIC 0x07738135U
#define RA4M1_PRCR_KEY 0xA500U
#define RA4M1_PRCR_PRC1_UNLOCK (RA4M1_PRCR_KEY | 0x2U)
#define RA4M1_PRCR_LOCK (RA4M1_PRCR_KEY | 0x0U)
#endif

#if defined(XIAO_RUNTIME_HAS_NRF52_BOOTMODE)
#define NRF52_BOOTLOADER_MAGIC 0x57
#endif

int xiao_board_runtime_init(void)
{
#if defined(CONFIG_USB_DEVICE_STACK) && !defined(CONFIG_USB_DEVICE_STACK_NEXT)
	int ret;

	ret = usb_enable(NULL);
	if (ret != 0) {
		printk("USB device initialization failed: %d\n", ret);
		return ret;
	}
#endif

	return 0;
}

#if defined(XIAO_RUNTIME_HAS_BOOTLOADER_REQUEST)
/* Requests the board bootloader path, then performs a cold reboot. */
/* 请求板级 bootloader 入口，然后执行冷重启。 */
static void xiao_request_bootloader(void)
{
#if defined(XIAO_RUNTIME_HAS_RETENTION_BOOTMODE)
	int ret;

	ret = bootmode_set(BOOT_MODE_TYPE_BOOTLOADER);
	if (ret < 0) {
		printk("Bootloader request failed: %d\n", ret);
		return;
	}
	printk("Rebooting to UF2 bootloader.\n");
	k_sleep(K_MSEC(50));
	sys_reboot(SYS_REBOOT_COLD);
#elif defined(XIAO_RUNTIME_HAS_RA4M1_BOOTMODE)
	R_SYSTEM->PRCR = (uint16_t)RA4M1_PRCR_PRC1_UNLOCK;
	*((volatile uint32_t *)&R_SYSTEM->VBTBKR[0]) = RA4M1_BOOTLOADER_MAGIC;
	R_SYSTEM->PRCR = (uint16_t)RA4M1_PRCR_LOCK;
	R_USB_FS0->SYSCFG_b.DPRPU = 0U;
	sys_reboot(SYS_REBOOT_COLD);
#elif defined(XIAO_RUNTIME_HAS_NRF52_BOOTMODE)
	nrf_power_gpregret_set(NRF_POWER, 0, NRF52_BOOTLOADER_MAGIC);
	printk("Rebooting to UF2 bootloader.\n");
	k_sleep(K_MSEC(50));
	sys_reboot(SYS_REBOOT_COLD);
#endif
}
#endif

void xiao_board_runtime_poll(void)
{
#if defined(XIAO_RUNTIME_HAS_BOOTLOADER_REQUEST)
	uint32_t baudrate = 0U;
	int ret;

	if (!device_is_ready(xiao_cdc_uart)) {
		return;
	}

	ret = uart_line_ctrl_get(xiao_cdc_uart, UART_LINE_CTRL_BAUD_RATE, &baudrate);
	if (ret == 0 && baudrate == XIAO_BOOTLOADER_BAUD_RATE) {
		xiao_request_bootloader();
	}
#endif
}

void xiao_board_runtime_sleep_ms(int32_t sleep_time_ms)
{
	int32_t remaining_ms = sleep_time_ms;

	while (remaining_ms > 0) {
		int32_t interval_ms = remaining_ms > XIAO_BOOTLOADER_POLL_INTERVAL_MS
					      ? XIAO_BOOTLOADER_POLL_INTERVAL_MS
					      : remaining_ms;

		k_msleep(interval_ms);
		xiao_board_runtime_poll();
		remaining_ms -= interval_ms;
	}
}
