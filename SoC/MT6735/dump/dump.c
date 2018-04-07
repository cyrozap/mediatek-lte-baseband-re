#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>

#include <sys/mman.h>


int main(int argc, char *argv[])
{
	int fd;
	void *map;
	volatile uint32_t *regs;

	uint32_t address;
	uint32_t reg_base;
	uint32_t reg_offset;
	uint32_t length;
	uint32_t pages;

	if (argc < 3 || argc > 3) {
		fprintf(stderr, "Usage: %s address length\n", argv[0]);
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

	if (sscanf(argv[2], "%x", &length) != 1) {
		fprintf(stderr, "Error: length \"%s\" is not an integer\n", argv[2]);
		return -1;
	}

	if (length % 4 != 0) {
		fprintf(stderr, "Error: length 0x%08x must be a multiple of 4\n", length);
		return -1;
	}

	long page_size = sysconf(_SC_PAGESIZE);
	reg_offset = address % page_size;
	reg_base = address - reg_offset;
	pages = ((reg_offset + length + (page_size - 1)) / page_size);
	//fprintf(stderr, "reg_offset = 0x%08x, reg_base = 0x%08x, pages = %d\n", reg_offset, reg_base, pages);

	if ((fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
		perror("can't open /dev/mem");
		return -1;
	}

	map = mmap(
		NULL,
		page_size * pages,
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

	for (uint32_t i = 0; i < length; i += 4) {
		printf("*0x%08x = 0x%08x\n", address+i, regs[(reg_offset+i)/4]);
	}

	return 0;
}
