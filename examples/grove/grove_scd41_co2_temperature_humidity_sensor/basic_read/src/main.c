/*
 * Grove SCD41 basic_read example.
 * Periodically samples CO2, temperature, and relative humidity from the SCD41
 * sensor and prints them over the console. The sensor binding comes from
 * app.overlay via the board-agnostic xiao_i2c connector label.
 *
 * Grove SCD41 basic_read 示例。
 * 周期性采样 SCD41 的 CO2、温度与相对湿度并打印到控制台。
 * 传感器绑定来自 app.overlay,通过板级无关的 xiao_i2c connector 标签。
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/sys/printk.h>

/* SCD41 single-shot measurement needs up to 5 seconds to produce a reading. */
/* SCD41 单次测量最长需要 5 秒才能产生一次读数。 */
#define SAMPLE_INTERVAL_MS 5000

static const struct device *const scd41 = DEVICE_DT_GET(DT_NODELABEL(scd41));

static void print_sample(const struct device *dev)
{
	struct sensor_value co2;
	struct sensor_value temp;
	struct sensor_value hum;

	if (sensor_sample_fetch(dev) < 0) {
		printk("SCD41 sample fetch failed\n");
		return;
	}

	sensor_channel_get(dev, SENSOR_CHAN_CO2, &co2);
	sensor_channel_get(dev, SENSOR_CHAN_AMBIENT_TEMP, &temp);
	sensor_channel_get(dev, SENSOR_CHAN_HUMIDITY, &hum);

	printk("CO2: %d ppm  Temp: %d.%06d C  RH: %d.%06d %%\n",
	       co2.val1,
	       temp.val1, temp.val2,
	       hum.val1, hum.val2);
}

int main(void)
{
	printk("*** Seeed XIAO Zephyr Base | grove: SCD41 basic_read | board: %s ***\n",
	       CONFIG_BOARD);

	if (!device_is_ready(scd41)) {
		printk("SCD41 device is not ready\n");
		return 0;
	}

	while (1) {
		print_sample(scd41);
		k_msleep(SAMPLE_INTERVAL_MS);
	}

	return 0;
}
