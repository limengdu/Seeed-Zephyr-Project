#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

int main(void)
{
	printk("*** Seeed XIAO Zephyr Base | board: %s | demo: %s ***\n", CONFIG_BOARD, "hello_world");

	while (1) {
		printk("Seeed XIAO hello_world demo is running.\n");
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
