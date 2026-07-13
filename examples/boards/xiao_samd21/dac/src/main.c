#include <stdbool.h>

#include <zephyr/device.h>
#include <zephyr/drivers/dac.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/usb/usb_device.h>

#define CONSOLE_NODE DT_CHOSEN(zephyr_console)
#define DAC_NODE DT_NODELABEL(dac0)
#define DAC_CHANNEL_ID 0
#define DAC_RESOLUTION 10
#define DAC_MAX_VALUE ((1U << DAC_RESOLUTION) - 1U)
#define DAC_STEP_DELAY_MS 2
#define DAC_LOG_INTERVAL 128

static const struct device *const console_dev = DEVICE_DT_GET(CONSOLE_NODE);
static const struct device *const dac_dev = DEVICE_DT_GET(DAC_NODE);

static const struct dac_channel_cfg dac_cfg = {
	.channel_id = DAC_CHANNEL_ID,
	.resolution = DAC_RESOLUTION,
};

/* Returns whether the host serial monitor has asserted USB CDC DTR.
 * 返回主机串口监视器是否已置位 USB CDC DTR。
 */
static bool console_is_connected(void)
{
	uint32_t dtr = 0U;

	return device_is_ready(console_dev) &&
	       uart_line_ctrl_get(console_dev, UART_LINE_CTRL_DTR, &dtr) == 0 &&
	       dtr != 0U;
}

/* Prints the DAC status while the host serial monitor is connected.
 * 在主机串口监视器已连接时输出 DAC 状态。
 */
static void log_dac_status(uint32_t value, bool *was_connected)
{
	bool is_connected = console_is_connected();

	if (is_connected && !*was_connected) {
		printk("XIAO SAMD21 DAC ramp example started\n");
	}
	if (is_connected) {
		printk("DAC ramp value: %u\n", value);
	}

	*was_connected = is_connected;
}

int main(void)
{
	int ret;
	uint32_t value = 0;
	bool console_was_connected = false;

	ret = usb_enable(NULL);
	if (ret != 0) {
		printk("USB device initialization failed: %d\n", ret);
		return 0;
	}

	if (!device_is_ready(dac_dev)) {
		printk("DAC device is not ready\n");
		return 0;
	}

	ret = dac_channel_setup(dac_dev, &dac_cfg);
	if (ret != 0) {
		printk("DAC channel setup failed: %d\n", ret);
		return 0;
	}

	while (1) {
		ret = dac_write_value(dac_dev, DAC_CHANNEL_ID, value);
		if (ret != 0) {
			printk("DAC write failed: %d\n", ret);
			return 0;
		}

		if ((value % DAC_LOG_INTERVAL) == 0U) {
			log_dac_status(value, &console_was_connected);
		}

		if (value >= DAC_MAX_VALUE) {
			value = 0;
		} else {
			value++;
		}

		k_msleep(DAC_STEP_DELAY_MS);
	}

	return 0;
}
