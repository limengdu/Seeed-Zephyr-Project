/*
 * Grove Ultrasonic basic_read example.
 * Uses the Grove Ultrasonic Ranger single SIG pin: output a trigger pulse, then
 * switch the same pin to input and measure the echo pulse width.
 *
 * Grove Ultrasonic basic_read 示例。
 * 使用 Grove Ultrasonic Ranger 的单根 SIG 引脚：先输出触发脉冲，再把同一引脚
 * 切换为输入并测量 echo 高电平宽度。
 */

#include <errno.h>
#include <stdint.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/time_units.h>

#define TRIGGER_SETTLE_US 2
#define TRIGGER_PULSE_US 12
#define ECHO_START_TIMEOUT_US 5000
#define ECHO_HIGH_TIMEOUT_US 38000
#define SAMPLE_INTERVAL_MS 1000

static const struct gpio_dt_spec signal =
	GPIO_DT_SPEC_GET(DT_PATH(zephyr_user), ultrasonic_gpios);

static int wait_for_level(int expected_level, uint32_t timeout_us, uint64_t *cycle_out)
{
	uint64_t start = k_cycle_get_64();

	while (k_cyc_to_us_floor64(k_cycle_get_64() - start) < timeout_us) {
		int level = gpio_pin_get_dt(&signal);

		if (level < 0) {
			return level;
		}
		if (level == expected_level) {
			if (cycle_out != NULL) {
				*cycle_out = k_cycle_get_64();
			}
			return 0;
		}
	}

	return -ETIMEDOUT;
}

static int read_distance(uint32_t *distance_mm, uint32_t *echo_us)
{
	uint64_t rise_cycle;
	uint64_t fall_cycle;
	int ret;

	ret = gpio_pin_configure_dt(&signal, GPIO_OUTPUT_INACTIVE);
	if (ret < 0) {
		return ret;
	}

	k_busy_wait(TRIGGER_SETTLE_US);

	ret = gpio_pin_set_dt(&signal, 1);
	if (ret < 0) {
		return ret;
	}

	k_busy_wait(TRIGGER_PULSE_US);

	ret = gpio_pin_set_dt(&signal, 0);
	if (ret < 0) {
		return ret;
	}

	ret = gpio_pin_configure_dt(&signal, GPIO_INPUT);
	if (ret < 0) {
		return ret;
	}

	ret = wait_for_level(1, ECHO_START_TIMEOUT_US, &rise_cycle);
	if (ret < 0) {
		return ret;
	}

	ret = wait_for_level(0, ECHO_HIGH_TIMEOUT_US, &fall_cycle);
	if (ret < 0) {
		return ret;
	}

	*echo_us = (uint32_t)k_cyc_to_us_floor64(fall_cycle - rise_cycle);
	*distance_mm = ((*echo_us * 17U) + 50U) / 100U;

	return 0;
}

int main(void)
{
	printk("*** Seeed XIAO Zephyr Base | grove: Ultrasonic basic_read | board: %s ***\n",
	       CONFIG_BOARD);
	printk("Signal pin comes from /zephyr,user ultrasonic-gpios\n");

	if (!gpio_is_ready_dt(&signal)) {
		printk("Ultrasonic GPIO device is not ready\n");
		return 0;
	}

	while (1) {
		uint32_t distance_mm = 0;
		uint32_t echo_us = 0;
		int ret = read_distance(&distance_mm, &echo_us);

		if (ret == -ETIMEDOUT) {
			printk("Distance: timeout\n");
		} else if (ret < 0) {
			printk("Distance: read failed (%d)\n", ret);
		} else {
			printk("Distance: %u.%u cm  Echo: %u us\n",
			       distance_mm / 10U, distance_mm % 10U, echo_us);
		}

		k_msleep(SAMPLE_INTERVAL_MS);
	}

	return 0;
}
