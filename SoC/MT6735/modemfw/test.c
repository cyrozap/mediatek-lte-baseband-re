#include <stdint.h>

volatile uint32_t * const ap_base = (volatile uint32_t * const)(0x90000000);
volatile uint32_t * const smem = (volatile uint32_t * const)(0x03800000);
volatile uint32_t * const data = (volatile uint32_t * const)(0x00000000);

// These are just GPIO registers I'm using as generic un-cached memory.
#define AP2MD_REG 0x10211160
#define MD2AP_REG 0x10211150

static char getchar(void) {
	char ret;

	// Wait for the AP to set the "data valid" flag.
	while ((ap_base[AP2MD_REG/4] & 0x100) == 0);

	ret = ap_base[AP2MD_REG/4] & 0xff;
	ap_base[AP2MD_REG/4] &= 0xfffffeff;

	return ret;
}

static void putchar(char c) {
	// Wait for the AP to clear the "data valid" flag.
	while ((ap_base[MD2AP_REG/4] & 0x100) != 0);

	ap_base[MD2AP_REG/4] &= 0xffffff00;
	ap_base[MD2AP_REG/4] |= c;
	ap_base[MD2AP_REG/4] |= 0x100;
}

typedef enum {
	CMD_READ = 0x40,
	CMD_WRITE = 0x80,
} cmd_t;

typedef enum {
	STATE_IDLE,
	STATE_RECV_READ_ADDR,
	STATE_SEND_READ_DATA,
	STATE_RECV_WRITE_ADDR,
	STATE_RECV_WRITE_DATA,
} state_t;

void main(void) {
	// Enable JTAG on SD card port.
	ap_base[0x10211400/4] = 0x6db11249;

	// Clear registers.
	ap_base[AP2MD_REG/4] &= 0xfffffe00;
	ap_base[MD2AP_REG/4] &= 0xfffffe00;

	char c;
	state_t state = STATE_IDLE;
	uint32_t ra = 0;
	uint32_t rd = 0;
	uint32_t wa = 0;
	uint32_t wd = 0;
	uint8_t rab_idx = 0;
	uint8_t rdb_idx = 0;
	uint8_t wab_idx = 0;
	uint8_t wdb_idx = 0;

	while (1) {
		switch (state) {
		case STATE_IDLE:
			state = STATE_IDLE;
			ra = 0;
			rd = 0;
			wa = 0;
			wd = 0;
			rab_idx = 0;
			rdb_idx = 0;
			wab_idx = 0;
			wdb_idx = 0;
			c = getchar();
			if (c == CMD_READ) {
				state = STATE_RECV_READ_ADDR;
			} else if (c == CMD_WRITE) {
				state = STATE_RECV_WRITE_ADDR;
			}
			break;
		case STATE_RECV_READ_ADDR:
			c = getchar();
			ra |= c << (8 * rab_idx);
			if (rab_idx < 3) {
				rab_idx++;
				state = STATE_RECV_READ_ADDR;
			} else {
				rd = data[ra/4];
				rab_idx = 0;
				state = STATE_SEND_READ_DATA;
			}
			break;
		case STATE_SEND_READ_DATA:
			c = (rd >> (8 * rdb_idx)) & 0xff;
			putchar(c);
			if (rdb_idx < 3) {
				rdb_idx++;
				state = STATE_SEND_READ_DATA;
			} else {
				rdb_idx = 0;
				state = STATE_IDLE;
			}
			break;
		case STATE_RECV_WRITE_ADDR:
			c = getchar();
			wa |= c << (8 * wab_idx);
			if (wab_idx < 3) {
				wab_idx++;
				state = STATE_RECV_WRITE_ADDR;
			} else {
				wab_idx = 0;
				state = STATE_RECV_WRITE_DATA;
			}
			break;
		case STATE_RECV_WRITE_DATA:
			c = getchar();
			wd |= c << (8 * wdb_idx);
			if (wdb_idx < 3) {
				wdb_idx++;
				state = STATE_RECV_WRITE_DATA;
			} else {
				data[wa/4] = wd;
				wdb_idx = 0;
				state = STATE_IDLE;
			}
			break;
		default:
			state = STATE_IDLE;
			break;
		}
	}
}
