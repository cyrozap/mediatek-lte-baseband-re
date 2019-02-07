#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>

#include <sys/mman.h>


// These are just GPIO registers I'm using as generic un-cached memory.
#define AP2MD_REG 0x10211160
#define MD2AP_REG 0x10211150

typedef enum {
	CMD_READ = 0x40,
	CMD_WRITE = 0x80,
} cmd_t;

typedef struct mem_info_s {
		volatile uint32_t * regs;
		uint32_t ap2md_offset;
		uint32_t md2ap_offset;
} mem_info_t;

static void send_chr(mem_info_t * mem_info, char c) {
	volatile uint32_t * regs = mem_info->regs;
	uint32_t ap2md_offset = mem_info->ap2md_offset;

	printf("send_chr(0x%02X): Wait for TX buffer to become ready...\n", c);
	// Wait for the MD to clear the "data valid" flag.
	while ((regs[ap2md_offset/4] & 0x100) != 0);
	printf("send_chr(0x%02X): Sending...\n", c);

	regs[ap2md_offset/4] &= 0xffffff00;
	regs[ap2md_offset/4] |= c;
	regs[ap2md_offset/4] |= 0x100;
	printf("send_chr(0x%02X): Sent!\n", c);
}

static char recv_chr(mem_info_t * mem_info) {
	volatile uint32_t * regs = mem_info->regs;
	uint32_t md2ap_offset = mem_info->md2ap_offset;
	char ret;

	printf("recv_chr(): Waiting for data in RX buffer...\n");
	// Wait for the MD to set the "data valid" flag.
	while ((regs[md2ap_offset/4] & 0x100) == 0);
	printf("recv_chr(): Reading data...\n");

	ret = regs[md2ap_offset/4] & 0xff;
	regs[md2ap_offset/4] &= 0xfffffeff;
	printf("recv_chr(): Read 0x%02X.\n", ret);

	return ret;
}

static void mem_write(mem_info_t * mem_info, uint32_t addr, uint32_t data) {
	const uint32_t pkt_len = 9;
	const char buf[] = {
		CMD_WRITE,
		addr & 0xff, (addr >> 8) & 0xff, (addr >> 16) & 0xff, (addr >> 24) & 0xff,
		data & 0xff, (data >> 8) & 0xff, (data >> 16) & 0xff, (data >> 24) & 0xff,
	};
	printf("mem_write(0x%08X, 0x%08X): Sending packet: 0x%02X, 0x%02X, 0x%02X, 0x%02X, 0x%02X, 0x%02X, 0x%02X, 0x%02X, 0x%02X\n",
			addr, data, buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7], buf[8]);
	for (uint32_t i = 0; i < pkt_len; i++) {
		send_chr(mem_info, buf[i]);
	}
	printf("mem_write(0x%08X, 0x%08X): Done.\n", addr, data);
}

static uint32_t mem_read(mem_info_t * mem_info, uint32_t addr) {
	uint32_t ret = 0;
	const uint32_t pkt_len = 5;
	char buf[] = { CMD_READ, addr & 0xff, (addr >> 8) & 0xff, (addr >> 16) & 0xff, (addr >> 24) & 0xff };
	printf("mem_read(0x%08X): Sending packet: 0x%02X, 0x%02X, 0x%02X, 0x%02X, 0x%02X\n",
			addr, buf[0], buf[1], buf[2], buf[3], buf[4]);
	for (uint32_t i = 0; i < pkt_len; i++) {
		send_chr(mem_info, buf[i]);
	}
	printf("mem_read(0x%08X): Receiving data...\n", addr);
	for (uint32_t i = 0; i < 4; i++) {
		ret |= recv_chr(mem_info) << (8 * i);
	}
	printf("mem_read(0x%08X): Done.\n", addr);
	return ret;
}

int main(int argc, char *argv[])
{
	int fd;
	void *map;
	volatile uint32_t *regs;

	uint32_t address;
	uint32_t reg_base;
	uint32_t reg_offset;
	uint32_t value;

	if (argc < 2 || argc > 3) {
		fprintf(stderr, "Usage: %s address [value]\n", argv[0]);
		return -1;
	}

	if (sscanf(argv[1], "%x", &address) != 1) {
		fprintf(stderr, "Error: address \"%s\" is not an integer\n", argv[1]);
		return -1;
	}

	if (address % 4 != 0) {
		fprintf(stderr, "Error: address 0x%08x must be a multiple of 4\n", address);
		return -1;
	}

	if (argc == 3) {
		if (sscanf(argv[2], "%x", &value) != 1) {
			fprintf(stderr, "Error: value \"%s\" is not an integer\n", argv[2]);
			return -1;
		}
	}

	long page_size = sysconf(_SC_PAGESIZE);
	reg_offset = MD2AP_REG % page_size;
	reg_base = MD2AP_REG - reg_offset;

	if ((fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
		perror("can't open /dev/mem");
		return -1;
	}

	map = mmap(
		NULL,
		page_size,
		PROT_READ|PROT_WRITE,
		MAP_SHARED,
		fd,
		reg_base
	);
	if (map == (void *)(-1)) {
		perror("mmap failed");
		return -1;
	}

	regs = (volatile uint32_t *)map;

	mem_info_t mem_info = {
		.regs = regs,
		.ap2md_offset = reg_offset + AP2MD_REG - MD2AP_REG,
		.md2ap_offset = reg_offset,
	};

	printf("*0x%08x = 0x%08x\n", address, mem_read(&mem_info, address));
	if (argc == 3) {
		mem_write(&mem_info, address, value);
		printf("*0x%08x = 0x%08x\n", address, mem_read(&mem_info, address));
	}

	return 0;
}
