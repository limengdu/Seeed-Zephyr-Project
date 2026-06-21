#include <stdbool.h>
#include <stdint.h>

#include <bsp_api.h>

#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/reboot.h>

#define SLEEP_TIME_MS 1000
#define RA4M1_BOOTLOADER_BAUD_RATE 1200U
#define RA4M1_BOOTLOADER_MAGIC 0x07738135U
#define RA4M1_PRCR_KEY 0xA500U
#define RA4M1_PRCR_PRC1_UNLOCK (RA4M1_PRCR_KEY | 0x2U)
#define RA4M1_PRCR_LOCK (RA4M1_PRCR_KEY | 0x0U)
#define LED0_NODE DT_ALIAS(led0)
#define CDC_ACM_UART_NODE DT_NODELABEL(cdc_acm_uart0)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "This board demo requires a led0 devicetree alias."
#endif

#if !DT_NODE_HAS_STATUS(CDC_ACM_UART_NODE, okay)
#error "This board demo requires a cdc_acm_uart0 devicetree node."
#endif

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
static const struct device *const cdc_uart = DEVICE_DT_GET(CDC_ACM_UART_NODE);

/*
 * Stores the ROM bootloader request marker, disconnects USB, and resets.
 * 写入 ROM bootloader 请求标记，断开 USB，然后复位。
 */
static void request_bootloader(void)
{
	R_SYSTEM->PRCR = (uint16_t)RA4M1_PRCR_PRC1_UNLOCK;
	*((volatile uint32_t *)&R_SYSTEM->VBTBKR[0]) = RA4M1_BOOTLOADER_MAGIC;
	R_SYSTEM->PRCR = (uint16_t)RA4M1_PRCR_LOCK;
	R_USB_FS0->SYSCFG_b.DPRPU = 0U;
	sys_reboot(SYS_REBOOT_COLD);
}

static void reboot_if_bootloader_requested(void)
{
	uint32_t baudrate = 0U;

	if (!device_is_ready(cdc_uart)) {
		return;
	}

	if (uart_line_ctrl_get(cdc_uart, UART_LINE_CTRL_BAUD_RATE, &baudrate) != 0) {
		return;
	}

	if (baudrate == RA4M1_BOOTLOADER_BAUD_RATE) {
		request_bootloader();
	}
}

int main(void)
{
	printk("*** Seeed XIAO Zephyr Base | board: %s | demo: %s ***\n", CONFIG_BOARD, "blinky");

	int ret;
	bool led_is_on = true;

	if (!gpio_is_ready_dt(&led)) {
		printk("LED device is not ready.\n");
		return 0;
	}

	ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
	if (ret < 0) {
		printk("LED configuration failed: %d\n", ret);
		return 0;
	}

	while (1) {
		ret = gpio_pin_toggle_dt(&led);
		if (ret < 0) {
			printk("LED toggle failed: %d\n", ret);
			return 0;
		}

		led_is_on = !led_is_on;
		printk("LED state: %s\n", led_is_on ? "ON" : "OFF");
		reboot_if_bootloader_requested();
		k_msleep(SLEEP_TIME_MS);
	}

	return 0;
}
