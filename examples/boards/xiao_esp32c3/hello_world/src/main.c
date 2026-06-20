#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

int main(void)
{
	while (1) {
		printk("Seeed XIAO hello_world demo is running.\n");
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
