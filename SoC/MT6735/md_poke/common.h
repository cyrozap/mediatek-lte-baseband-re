#ifndef COMMON_H
#define COMMON_H

typedef enum {
	CMD_READ = 0x40,
	CMD_WRITE = 0x80,
} cmd_t;

typedef struct mem_info_s {
		volatile uint32_t * regs;
		uint32_t ap2md_offset;
		uint32_t md2ap_offset;
} mem_info_t;

void mem_write(mem_info_t * mem_info, uint32_t addr, uint32_t data);

uint32_t mem_read(mem_info_t * mem_info, uint32_t addr);

int get_mem_info(mem_info_t * mem_info);

#endif
