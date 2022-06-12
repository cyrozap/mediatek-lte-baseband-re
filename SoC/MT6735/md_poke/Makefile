# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2019  Forest Crossman <cyrozap@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


CC := arm-linux-gnueabihf-gcc
CFLAGS := -Wall -Werror -static

all: md_dump md_poke

md_dump: md_dump.o common.o
	$(CC) $(CFLAGS) -o $@ $^

md_poke: md_poke.o common.o
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

push: md_dump md_poke
	adb push $^ /data/local/tmp

clean:
	rm -f md_dump md_poke *.o

.PHONY: all clean push
