#include <stddef.h>
#include <stdint.h>

static uint32_t volatile * const mem = (uint32_t volatile * const)(0x00000000);
#define SRAM 0x00100000
#define L2_SRAM 0x00200000

static uint32_t UART_BASE;
static uint32_t UART_RBR;
static uint32_t UART_THR;
static uint32_t UART_LSR;

#define UART_LSR_DR   (1 << 0)
#define UART_LSR_THRE (1 << 5)

static uint32_t TOPRGU_BASE;
static uint32_t USBDL;

#define MAX_CMD_LEN 100
#define MAX_ARGS 3

extern char const * const build_version;
extern char const * const build_time;

static char const * soc_name;

static uint32_t readw(uint32_t reg) {
	return mem[reg/4];
}

static void writew(uint32_t reg, uint32_t word) {
	mem[reg/4] = word;
}

static char getchar(void) {
	char ret;

	// Wait for the UART to assert the "data ready" flag.
	while ((readw(UART_LSR) & UART_LSR_DR) == 0);

	ret = readw(UART_RBR) & 0xff;

	return ret;
}

static void putchar(char c) {
	// Wait for the UART to become ready.
	while ((readw(UART_LSR) & UART_LSR_THRE) == 0);

	if (c == '\n')
		putchar('\r');

	writew(UART_THR, c);
}

static void putbyte(uint8_t b) {
	// Wait for the UART to become ready.
	while ((readw(UART_LSR) & UART_LSR_THRE) == 0);

	writew(UART_THR, b);
}

static size_t strnlen(const char * buf, size_t max_len) {
	size_t len = 0;
	for (size_t i = 0; i < max_len; i++) {
		if (buf[i] == 0)
			break;
		len++;
	}
	return len;
}

static void print(const char * buf) {
	for (size_t i = 0; ; i++) {
		if (buf[i] == 0)
			break;
		putchar(buf[i]);
	}
}

static void println(const char * buf) {
	print(buf);
	putchar('\n');
}

static int strcmp (const char * str1, const char * str2) {
	int ret = 0;
	for (size_t i = 0; ; i++) {
		ret = str1[i] - str2[i];
		if (str1[i] == 0 || str2[i] == 0 || ret != 0) {
			break;
		}
	}
	return ret;
}

static int strncmp (const char * str1, const char * str2, size_t num) {
	int ret = 0;
	for (size_t i = 0; i < num; i++) {
		ret = str1[i] - str2[i];
		if (str1[i] == 0 || str2[i] == 0 || ret != 0) {
			break;
		}
	}
	return ret;
}

static void * memset (void * ptr, int value, size_t num) {
	for (size_t i = 0; i < num; i++) {
		((uint8_t *)ptr)[i] = (uint8_t)value;
	}

	return ptr;
}

static void setbaud(uint32_t baudrate);

static void init(void) {
	uint32_t soc_id = readw(0x08000000);
	switch(soc_id) {
	case 0x0279:
		soc_name = "MT6797";
		UART_BASE = 0x11002000;
		TOPRGU_BASE = 0x10007000;
		USBDL = 0x10001680;
		break;
	case 0x0321:
		soc_name = "MT6735";
		UART_BASE = 0x11002000;
		TOPRGU_BASE = 0x10212000;
		USBDL = 0x10000818;
		break;
	case 0x0335:
		soc_name = "MT6737M";
		UART_BASE = 0x11002000 + 0x1000; // UART1 base address.

		// Configure UART1 pins.
		uint32_t gpio_dir = readw(0x10211020);
		gpio_dir &= ~(1 << 12);
		gpio_dir |= (1 << 13);
		writew(0x10211020, gpio_dir);
		uint32_t gpio_pull_sel = readw(0x10211A50);
		gpio_pull_sel |= 1 << 15;
		writew(0x10211A50, gpio_pull_sel);
		uint32_t gpio_pull_en = readw(0x10211A30);
		gpio_pull_en |= 1 << 15;
		writew(0x10211A30, gpio_pull_sel);
		uint32_t gpio_mode = readw(0x10211370);
		gpio_mode &= ~((0x7 << 22) | (0x7 << 19));
		gpio_mode |= (0x1 << 22) | (0x1 << 19);
		writew(0x10211370, gpio_mode);

		// Configure UART1.
		setbaud(115200);

		TOPRGU_BASE = 0x10212000;
		USBDL = 0x10000818;
		break;
	case 0x8163:
		soc_name = "MT8163";
		UART_BASE = 0x11002000;
		TOPRGU_BASE = 0x10007000;
		USBDL = 0x10202050;
		break;
	default:
		soc_name = "UNKNOWN";
		UART_BASE = 0x11002000;
		TOPRGU_BASE = 0x10007000;
		USBDL = 0x10202050;
		break;
	}
	UART_RBR = UART_BASE + 0x00;
	UART_THR = UART_BASE + 0x00;
	UART_LSR = UART_BASE + 0x14;

	// Make sure WDT is disabled.
	writew(TOPRGU_BASE, 0x22000000);
}

static int parse_dec(uint32_t * value, const char * str) {
	size_t len = strnlen(str, 11);
	if (len > 10) {
		println("Error: Decimal string too long.");
		return -1;
	}

	*value = 0;
	uint32_t multiplier = 1;
	for (size_t i = 0; i < len; i++) {
		char c = str[len - i - 1];
		if ('0' <= c && c <= '9') {
			uint8_t digit = c - '0';
			*value += digit * multiplier;
			multiplier *= 10;
		} else {
			print("Error: Bad character in decimal string: ");
			putchar(c);
			putchar('\n');
			return -1;
		}
	}

	return 0;
}

static int parse_hex(uint32_t * value, const char * str) {
	size_t start = 0;
	if (str[0] == '0' && (str[1] == 'x' || str[1] == 'X')) {
		start = 2;
	}

	size_t len = strnlen(&str[start], 18-start);
	if (len > 8) {
		println("Error: Hex string too long.");
		return -1;
	}

	*value = 0;
	for (size_t i = start; i < len + start; i++) {
		uint8_t nybble = 0;
		if ('a' <= str[i] && str[i] <= 'f') {
			nybble = str[i] - 'a' + 0xa;
		} else if ('A' <= str[i] && str[i] <= 'F') {
			nybble = str[i] - 'A' + 0xa;
		} else if ('0' <= str[i] && str[i] <= '9') {
			nybble = str[i] - '0';
		} else {
			print("Error: Bad character in hex string: ");
			putchar(str[i]);
			putchar('\n');
			return -1;
		}

		*value |= nybble << (4 * (len + start - i - 1));
	}

	return 0;
}

static void print_dec(size_t value, size_t min_digits) {
	size_t digits = 0;
	for (size_t remaining = value; remaining != 0; remaining /= 10) {
		digits++;
	}
	if (value == 0) {
		digits = 1;
	}
	if (min_digits > 0 && min_digits > digits) {
		digits = min_digits;
	}
	for (size_t i = 0; i < digits; i++) {
		size_t digit = value;
		for (size_t d = 1; d < digits - i; d++) {
			digit /= 10;
		}
		uint8_t chr = (digit % 10) + '0';
		putchar(chr);
	}
}

static void print_hex(size_t value, size_t min_digits) {
	size_t digits = 0;
	for (size_t remaining = value; remaining != 0; remaining >>= 4) {
		digits++;
	}
	if (value == 0) {
		digits = 1;
	}
	if (min_digits > 0 && min_digits > digits) {
		digits = min_digits;
	}

	putchar('0');
	putchar('x');
	for (size_t i = 0; i < digits; i++) {
		uint8_t nybble = (value >> (4 * (digits - i - 1))) & 0xf;
		uint8_t chr = 0;
		if (0 <= nybble && nybble <= 9) {
			chr = nybble + '0';
		} else if (0xa <= nybble && nybble <= 0xf) {
			chr = nybble - 0xa + 'a';
		} else {
			chr = '?';
		}
		putchar(chr);
	}
}

static int mrw_handler(size_t argc, const char * argv[]) {
	if (argc < 2) {
		println("Error: Too few arguments.");
		println("Usage: mrw address");
		println("Examples:");
		println("    mrw 0x00000000");
		println("    mrw 0x8");
		println("    mrw 00000");
		println("    mrw c");
		println("    mrw 00201000");
		println("    mrw 201000");
		return -1;
	}

	uint32_t ptr = 0;
	int ret = parse_hex(&ptr, argv[1]);
	if (ret != 0) {
		println("Error: parse_hex() failed.");
		return -1;
	}
	if (ptr % 4) {
		println("Error: address must be 4-byte aligned.");
		return -1;
	}
	print_hex(ptr, 8);
	print(": ");

	uint32_t value = readw(ptr);
	print_hex(value, 8);
	putchar('\n');

	return 0;
}

static int mww_handler(size_t argc, const char * argv[]) {
	if (argc < 3) {
		println("Error: Too few arguments.");
		println("Usage: mww address value");
		println("Examples:");
		println("    mww 0x00200000 0");
		println("    mww 0x100008 1234");
		println("    mww 100000 0x008");
		println("    mww 20100c 0x1");
		println("    mww 00201000 0");
		return -1;
	}

	int ret = 0;

	uint32_t ptr = 0;
	ret = parse_hex(&ptr, argv[1]);
	if (ret != 0) {
		println("Error: parse_hex(argv[1]) failed.");
		return -1;
	}
	if (ptr % 4) {
		println("Error: address must be 4-byte aligned.");
		return -1;
	}
	print_hex(ptr, 8);
	print(": ");
	print_hex(readw(ptr), 8);
	putchar('\n');

	uint32_t value = 0;
	ret = parse_hex(&value, argv[2]);
	if (ret != 0) {
		println("Error: parse_hex(argv[2]) failed.");
		return -1;
	}
	writew(ptr, value);

	print_hex(ptr, 8);
	print(": ");
	print_hex(readw(ptr), 8);
	putchar('\n');

	return ret;
}

static void setbaud(uint32_t baudrate) {
	// Set high speed mode.
	writew(UART_BASE + 0x24, 0x3);

	// Calculate parameters.
	uint32_t cpu_freq_hz = 26000000;
	uint32_t tmp = (cpu_freq_hz + (baudrate / 2)) / baudrate;
	uint32_t divisor_latch = ((tmp + 255) >> 8);
	uint32_t sample_count = tmp / divisor_latch;

	// Write sample count.
	writew(UART_BASE + 0x28, (sample_count - 1) & 0xff);

	// Write sample point.
	writew(UART_BASE + 0x2c, ((sample_count - 1) / 2) & 0xff);

	// Write divisor latch.
	writew(UART_BASE + 0xc, 0x80);
	writew(UART_BASE + 0x0, divisor_latch & 0xff);
	writew(UART_BASE + 0x4, (divisor_latch >> 8) & 0xff);

	// Configure UART parameters: 8N1
	writew(UART_BASE + 0xc, 0x3);

	// Configure and initialize FIFO.
	writew(UART_BASE + 0x8, 0x97);
}

static int setbaud_handler(size_t argc, const char * argv[]) {
	if (argc < 2) {
		println("Error: Too few arguments.");
		println("Usage: setbaud baudrate");
		println("Examples:");
		println("    setbaud 115200");
		println("    setbaud 921600");
		return -1;
	}

	uint32_t baudrate;
	int ret = parse_dec(&baudrate, argv[1]);
	if (ret != 0) {
		println("Error: parse_dec(argv[1]) failed.");
		return -1;
	}

	if (baudrate < 115200 || 921600 < baudrate) {
		println("Error: baudrate must be between 115200 and 921600, inclusive.");
		return -1;
	}

	setbaud(baudrate);

	return 0;
}

static int reset_handler(size_t argc, const char * argv[]) {
	println("Resetting SoC...");

	// Wait for the UART to finish printing.
	while ((readw(UART_LSR) & UART_LSR_THRE) == 0);

	writew(TOPRGU_BASE, 0x22000000 | 0x10 | 0x4);
	writew(TOPRGU_BASE + 0x14, 0x1209);

	return 0;
}

static int usbdl_handler(size_t argc, const char * argv[]) {
	if (argc < 2) {
		println("Error: Too few arguments.");
		println("Usage: usbdl {enable,disable,now} [timeout]");
		println("Examples:");
		println("    usbdl enable none");
		println("    usbdl enable 60");
		println("    usbdl enable");
		println("    usbdl disable");
		println("    usbdl now none");
		println("    usbdl now 60");
		println("    usbdl now");
		return -1;
	}

	if (!strcmp(argv[1], "enable")) {
		uint32_t timeout = 60; // 0x3fff is no timeout. Less than that is timeout in seconds.
		if (argc > 2) {
			if (!strcmp(argv[2], "none")) {
				timeout = 0x3fff;
			} else {
				int ret = parse_dec(&timeout, argv[2]);
				if (ret != 0) {
					println("Error: parse_dec(argv[2]) failed.");
					return -1;
				}
				if (timeout >= 0x3fff) {
					println("Error: timeout must be less than 16383 seconds.");
					return -1;
				}
			}
		}

		print("Configuring SoC to enter BROM DL mode on reset, with ");
		if (timeout == 0x3fff) {
			println("no timeout.");
		} else {
			print("a timeout of ");
			print_dec(timeout, 0);
			println(" seconds.");
		}

		// Write USBDL flag.
		uint32_t usbdl_flag = (0x444C << 16) | (timeout << 2) | 0x00000001; // USBDL_BIT_EN
		writew(USBDL + 0x00, usbdl_flag);  // USBDL_FLAG/BOOT_MISC0

		// Make sure USBDL_FLAG is not reset by the WDT.
		writew(USBDL + 0x20, 0xAD98);  // MISC_LOCK_KEY
		writew(USBDL + 0x28, 0x00000001);  // RST_CON
		writew(USBDL + 0x20, 0);  // MISC_LOCK_KEY
	} else if (!strcmp(argv[1], "disable")) {
		// Make sure USBDL_FLAG is reset by the WDT.
		writew(USBDL + 0x20, 0xAD98);  // MISC_LOCK_KEY
		writew(USBDL + 0x28, 0x00000000);  // RST_CON
		writew(USBDL + 0x20, 0);  // MISC_LOCK_KEY
	} else if (!strcmp(argv[1], "now")) {
		const char * new_argv[] = { argv[0], "enable", argv[2] };
		int ret = usbdl_handler(argc, new_argv);
		if (ret != 0) {
			return ret;
		}
		return reset_handler(0, NULL);
	} else {
		print("Error: Unknown subcommand: ");
		println(argv[1]);
		return -1;
	}

	return 0;
}

typedef enum bmo_commands {
	EXIT = '\r',
	READ = 'R',
	WRITE = 'W',
	SETBAUD = 'S',
	MEM_READ = 'r',
	MEM_WRITE = 'w',
} bmo_command_t;

static int bmo_handler(size_t argc, const char * argv[]) {
	int ret = 0;
	int done = 0;

	println("OK");
	while (!done) {
		uint32_t addr = 0;
		uint32_t val = 0;
		uint32_t len = 0;
		bmo_command_t command = getchar();
		switch (command) {
		case EXIT:
			done = 1;
			break;
		case READ:
			for (int i = 0; i < 4; i++) {
				addr |= getchar() << (i * 8);
			}
			val = readw(addr);
			for (int i = 0; i < 4; i++) {
				putbyte((val >> (i * 8)) & 0xff);
			}
			break;
		case WRITE:
			for (int i = 0; i < 4; i++) {
				addr |= getchar() << (i * 8);
			}
			for (int i = 0; i < 4; i++) {
				val |= getchar() << (i * 8);
			}
			writew(addr, val);
			break;
		case SETBAUD:
			for (int i = 0; i < 4; i++) {
				val |= getchar() << (i * 8);
			}
			setbaud(val);
			break;
		case MEM_READ:
			for (int i = 0; i < 4; i++) {
				addr |= getchar() << (i * 8);
			}
			for (int i = 0; i < 4; i++) {
				len |= getchar() << (i * 8);
			}
			for (uint32_t off = 0; off < len; off += 4) {
				val = readw(addr + off);
				for (int i = 0; i < 4; i++) {
					putbyte((val >> (i * 8)) & 0xff);
				}
			}
			break;
		case MEM_WRITE:
			for (int i = 0; i < 4; i++) {
				addr |= getchar() << (i * 8);
			}
			for (int i = 0; i < 4; i++) {
				len |= getchar() << (i * 8);
			}
			for (uint32_t off = 0; off < len; off += 4) {
				val = 0;
				for (int i = 0; i < 4; i++) {
					val |= getchar() << (i * 8);
				}
				writew(addr + off, val);
			}
			break;
		default:
			break;
		}
	}
	return ret;
}

static int version_handler(size_t argc, const char * argv[]) {
	print("Build version: ");
	println(build_version);
	print("Build time: ");
	println(build_time);
	print("SoC name: ");
	println(soc_name);
	return 0;
}

static int help_handler(size_t argc, const char * argv[]);

typedef struct {
	char * command;
	int (* handler)(size_t, const char **);
} command;

static const command cmd_table[] = {
	{ "help", help_handler },
	{ "version", version_handler },
	{ "mrw", mrw_handler },
	{ "mww", mww_handler },
	{ "setbaud", setbaud_handler },
	{ "reset", reset_handler },
	{ "usbdl", usbdl_handler },
	{ "bmo", bmo_handler },
	{ 0, 0 },
};

static int help_handler(size_t argc, const char * argv[]) {
	println("Commands available:");
	for (size_t i = 0; cmd_table[i].command != 0; i++) {
		print(" - ");
		println(cmd_table[i].command);
	}
	return 0;
}

static int handle_command(size_t argc, const char * argv[]) {
	if (argc > 0) {
		for (size_t i = 0; cmd_table[i].command != 0; i++) {
			if (!strncmp(argv[0], cmd_table[i].command, MAX_CMD_LEN)) {
				return cmd_table[i].handler(argc, argv);
			}
		}
		print("Error: Unknown command: ");
		println(argv[0]);
	}

	return -1;
}

static int parse_cmdline(char * buf) {
	size_t argc = 0;
	const char * argv[MAX_ARGS] = { 0 };

	for (size_t i = 0; i < MAX_CMD_LEN + 1 && argc != MAX_ARGS; i++) {
		switch (buf[i]) {
		case 0:
		case ' ':
		case '\t':
			if (argv[argc] != 0) {
				buf[i] = 0;
				argc++;
			}
			break;
		default:
			if (argv[argc] == 0) {
				argv[argc] = &buf[i];
			}
			break;
		}
	}

	return handle_command(argc, argv);
}

static void cmdloop(void) {
	while (1) {
		print("> ");
		char cmd_buf[MAX_CMD_LEN + 1] = { 0 };
		size_t cmd_len = 0;
		int cmd_entered = 0;
		while (!cmd_entered) {
			char c = getchar();
			switch (c) {
			case 0x1b:
				// Escape sequences.
				c = getchar();
				switch (c) {
				case '[':
					c = getchar();
					switch (c) {
					case 'A':
					case 'B':
					case 'C':
					case 'D':
						// Arrow keys.
						break;
					case '1':
					case '2':
					case '3':
					case '4':
					case '5':
					case '6':
						// Paging.
						getchar();
						break;
					default:
						print("^[[");
						putchar(c);
					}
					break;
				case 'O':
					c = getchar();
					switch (c) {
					case 'F':
						// End key.
						break;
					default:
						print("^[O");
						putchar(c);
					}
					break;
				default:
					print("^[");
					putchar(c);
				}
				break;
			case '\r':
				// Newline.
				cmd_buf[cmd_len] = 0;
				cmd_entered = 1;
				break;
			case '\b':
				// Backspace.
				if (cmd_len > 0) {
					print("\b \b");
					cmd_buf[--cmd_len] = 0;
				}
				break;
			case 0x03:
				// Control-C
				memset(cmd_buf, 0, MAX_CMD_LEN + 1);
				cmd_entered = 1;
				break;
			default:
				if (cmd_len < MAX_CMD_LEN) {
					putchar(c);
					cmd_buf[cmd_len++] = c;
				}
			}
		}
		putchar('\n');
		parse_cmdline(cmd_buf);
	}
}

int main(void) {
	init();
	println("Hello from AArch64!");
	print("hello-aarch64 version ");
	print(build_version);
	print(" (built on ");
	print(build_time);
	println(")");
	cmdloop();
	return 0;
}
