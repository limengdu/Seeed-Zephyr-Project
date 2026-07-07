#ifndef XIAO_BOARD_RUNTIME_H_
#define XIAO_BOARD_RUNTIME_H_

#include <stdint.h>

int xiao_board_runtime_init(void);
void xiao_board_runtime_poll(void);
void xiao_board_runtime_sleep_ms(int32_t sleep_time_ms);

#endif /* XIAO_BOARD_RUNTIME_H_ */
