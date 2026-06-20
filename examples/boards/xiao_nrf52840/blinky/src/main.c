#include <stdbool.h>
#include <stdint.h>

#include <hal/nrf_power.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/reboot.h>

#define SLEEP_TIME_MS 1000
#define BOOTLOADER_BAUD_RATE 1200
#define BOOTLOADER_POLL_INTERVAL_MS 50
#define NRF52_BOOTLOADER_MAGIC 0x57
#define LED0_NODE DT_ALIAS(led0)
#define CDC_ACM_NODE DT_NODELABEL(board_cdc_acm_uart)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "This board demo requires a led0 devicetree alias."
#endif

#if !DT_NODE_HAS_STATUS(CDC_ACM_NODE, okay)
#error "This board demo requires a USB CDC ACM UART node."
#endif

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
static const struct device *const cdc_acm = DEVICE_DT_GET(CDC_ACM_NODE);

/* Requests the Adafruit nRF52 UF2 bootloader path and reboots.
 * 请求 Adafruit nRF52 UF2 bootloader 路径并重启。
 */
static void reboot_to_bootloader(void)
{
	nrf_power_gpregret_set(NRF_POWER, 0, NRF52_BOOTLOADER_MAGIC);
	printk("Rebooting to UF2 bootloader.\n");
	k_sleep(K_MSEC(50));
	sys_reboot(SYS_REBOOT_COLD);
}

/* Enters UF2 bootloader mode when the host opens USB CDC at 1200 baud.
 * 当主机以 1200 baud 打开 USB CDC 时，进入 UF2 bootloader 模式。
 */
static void handle_bootloader_request(void)
{
	uint32_t baudrate;
	int ret;

	if (!device_is_ready(cdc_acm)) {
		return;
	}

	ret = uart_line_ctrl_get(cdc_acm, UART_LINE_CTRL_BAUD_RATE, &baudrate);
	if (ret == 0 && baudrate == BOOTLOADER_BAUD_RATE) {
		reboot_to_bootloader();
	}
}

/* Sleeps in short intervals so USB CDC bootloader requests are not missed.
 * 以短间隔休眠，避免错过 USB CDC bootloader 请求。
 */
static void sleep_with_bootloader_checks(int sleep_time_ms)
{
	int remaining_ms = sleep_time_ms;

	while (remaining_ms > 0) {
		int interval_ms = remaining_ms > BOOTLOADER_POLL_INTERVAL_MS
					  ? BOOTLOADER_POLL_INTERVAL_MS
					  : remaining_ms;

		k_msleep(interval_ms);
		handle_bootloader_request();
		remaining_ms -= interval_ms;
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
		handle_bootloader_request();

		ret = gpio_pin_toggle_dt(&led);
		if (ret < 0) {
			printk("LED toggle failed: %d\n", ret);
			return 0;
		}

		led_is_on = !led_is_on;
		printk("LED state: %s\n", led_is_on ? "ON" : "OFF");
		sleep_with_bootloader_checks(SLEEP_TIME_MS);
	}

	return 0;
}
