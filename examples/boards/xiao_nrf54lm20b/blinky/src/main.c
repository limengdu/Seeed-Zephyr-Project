#include <stdbool.h>

#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/kernel.h>
#include <zephyr/retention/bootmode.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/reboot.h>

#define SLEEP_TIME_MS 1000
#define LOADER_POLL_INTERVAL_MS 50
#define LOADER_BAUD_RATE 1200U
#define LED0_NODE DT_ALIAS(led0)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "This board demo requires a led0 devicetree alias."
#endif

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
static const struct device *const cdc_acm = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

/* Records a firmware-loader request and cold-reboots the processor.
 * 记下固件加载器请求，并冷复位处理器。
 */
static void reboot_to_loader(void)
{
	if (bootmode_set(BOOT_MODE_TYPE_BOOTLOADER) != 0) {
		return;
	}
	sys_reboot(SYS_REBOOT_COLD);
}

/* Polls USB CDC line settings during the LED interval.
 * 在 LED 切换间隔内轮询 USB CDC 串口设置。
 */
static void sleep_with_loader_checks(void)
{
	for (int elapsed_ms = 0; elapsed_ms < SLEEP_TIME_MS;
	     elapsed_ms += LOADER_POLL_INTERVAL_MS) {
		uint32_t baudrate = 0U;

		if (device_is_ready(cdc_acm) &&
		    uart_line_ctrl_get(cdc_acm, UART_LINE_CTRL_BAUD_RATE, &baudrate) == 0 &&
		    baudrate == LOADER_BAUD_RATE) {
			reboot_to_loader();
		}
		k_msleep(LOADER_POLL_INTERVAL_MS);
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
		sleep_with_loader_checks();
	}

	return 0;
}
