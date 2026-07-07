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

#include "xiao_board_runtime.h"

#define TRIGGER_SETTLE_US 2
#define TRIGGER_PULSE_US 5
#define PULSE_TIMEOUT_US 1000000
#define MIN_VALID_ECHO_US 100
#define POLL_STEP_US 1
#define SAMPLE_INTERVAL_MS 1000

static const struct gpio_dt_spec signal =
	GPIO_DT_SPEC_GET(DT_PATH(zephyr_user), ultrasonic_gpios);

static uint32_t elapsed_us_since(uint32_t start_cycle)
{
	/* Converts the current cycle-counter delta to elapsed microseconds. */
	/* 将当前时钟周期差换算为已经过去的微秒数。 */
	return k_cyc_to_us_floor32(k_cycle_get_32() - start_cycle);
}

static int wait_while_level(int held_level, uint32_t start_cycle, uint32_t timeout_us)
{
	/* Waits for a previous pulse at the requested level to finish. */
	/* 等待指定电平上的上一段脉冲结束。 */
	int level;

	while (elapsed_us_since(start_cycle) < timeout_us) {
		level = gpio_pin_get_dt(&signal);
		if (level < 0) {
			return level;
		}
		if (level != held_level) {
			return 0;
		}

		k_busy_wait(POLL_STEP_US);
	}

	return -ETIMEDOUT;
}

static int wait_for_level(int expected_level, uint32_t start_cycle, uint32_t timeout_us,
				  uint32_t *cycle_out)
{
	/* Waits for SIG to reach the requested level and records the edge cycle. */
	/* 等待 SIG 到达指定电平，并记录边沿出现时的时钟周期。 */
	int level;

	while (elapsed_us_since(start_cycle) < timeout_us) {
		level = gpio_pin_get_dt(&signal);
		if (level < 0) {
			return level;
		}
		if (level == expected_level) {
			*cycle_out = k_cycle_get_32();
			return 0;
		}

		k_busy_wait(POLL_STEP_US);
	}

	return -ETIMEDOUT;
}

static int pulse_in_high(uint32_t timeout_us, uint32_t *pulse_us)
{
	/* Mirrors pulse-width capture semantics with Zephyr cycle timestamps. */
	/* 使用 Zephyr 时钟周期时间戳实现脉宽采集语义。 */
	uint32_t capture_start_cycle = k_cycle_get_32();
	uint32_t pulse_start_cycle;
	uint32_t pulse_end_cycle;
	uint32_t width_us;
	int ret;

	while (elapsed_us_since(capture_start_cycle) < timeout_us) {
		ret = wait_while_level(1, capture_start_cycle, timeout_us);
		if (ret < 0) {
			return ret;
		}

		ret = wait_for_level(1, capture_start_cycle, timeout_us, &pulse_start_cycle);
		if (ret < 0) {
			return ret;
		}

		ret = wait_for_level(0, capture_start_cycle, timeout_us, &pulse_end_cycle);
		if (ret < 0) {
			return ret;
		}

		width_us = k_cyc_to_us_floor32(pulse_end_cycle - pulse_start_cycle);
		if (width_us >= MIN_VALID_ECHO_US) {
			*pulse_us = width_us;
			return 0;
		}
	}

	return -ETIMEDOUT;
}

static int read_distance(uint32_t *distance_mm, uint32_t *echo_us)
{
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

	/* Release SIG and measure the HIGH echo pulse on the same pin. */
	/* 释放 SIG，并在同一引脚上测量 echo 高电平脉冲。 */
	ret = gpio_pin_configure_dt(&signal, GPIO_INPUT);
	if (ret < 0) {
		return ret;
	}

	ret = pulse_in_high(PULSE_TIMEOUT_US, echo_us);
	if (ret < 0) {
		return ret;
	}

	/* Distance in mm: echo microseconds / 29 / 2, scaled to mm. */
	*distance_mm = (*echo_us * 10U) / 58U;

	return 0;
}

int main(void)
{
	int ret;

	if (xiao_board_runtime_init() != 0) {
		return 0;
	}

	printk("*** Seeed XIAO Zephyr Base | grove: Ultrasonic basic_read | board: %s ***\n",
	       CONFIG_BOARD);
	printk("Signal pin comes from /zephyr,user ultrasonic-gpios\n");

	if (!gpio_is_ready_dt(&signal)) {
		printk("Ultrasonic GPIO device is not ready\n");
		return 0;
	}

	while (1) {
		xiao_board_runtime_poll();

		uint32_t distance_mm = 0;
		uint32_t echo_us = 0;

		ret = read_distance(&distance_mm, &echo_us);
		if (ret == -ETIMEDOUT) {
			printk("Distance: timeout\n");
		} else if (ret < 0) {
			printk("Distance: read failed (%d)\n", ret);
		} else {
			printk("Distance: %u.%u cm  Echo: %u us\n",
			       distance_mm / 10U, distance_mm % 10U, echo_us);
		}

		xiao_board_runtime_sleep_ms(SAMPLE_INTERVAL_MS);
	}

	return 0;
}
