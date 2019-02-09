#include <stdint.h>
#include <stdio.h>

#include "common.h"

int main(int argc, char *argv[])
{
	uint32_t address;
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

	mem_info_t mem_info;

	if (get_mem_info(&mem_info) != 0) {
		return -1;
	}

	printf("*0x%08x = 0x%08x\n", address, mem_read(&mem_info, address));
	if (argc == 3) {
		mem_write(&mem_info, address, value);
		printf("*0x%08x = 0x%08x\n", address, mem_read(&mem_info, address));
	}

	return 0;
}
