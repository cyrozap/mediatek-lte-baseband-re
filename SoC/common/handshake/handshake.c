#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

int set_interface_attribs(int fd, int speed)
{
    struct termios tty;

    if (tcgetattr(fd, &tty) < 0) {
        perror("Error from tcgetattr()");
        return -1;
    }

    cfsetospeed(&tty, (speed_t)speed);
    cfsetispeed(&tty, (speed_t)speed);

    //tty.c_cflag |= (CLOCAL | CREAD);    /* ignore modem controls */
    //tty.c_cflag &= ~CSIZE;
    //tty.c_cflag |= CS8;         /* 8-bit characters */
    //tty.c_cflag &= ~PARENB;     /* no parity bit */
    //tty.c_cflag &= ~CSTOPB;     /* only need 1 stop bit */
    //tty.c_cflag &= ~CRTSCTS;    /* no hardware flowcontrol */

    /* setup for non-canonical mode */
    //tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON);
    //tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
    //tty.c_oflag &= ~OPOST;

    /* Settings found using strace. */
    tty.c_iflag=0;
    tty.c_oflag=0x4;
    tty.c_cflag=0x10b2;
    tty.c_lflag=0xa30;

    /* fetch bytes as they become available */
    tty.c_cc[VMIN] = 1;
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        perror("Error from tcsetattr()");
        return -1;
    }
    return 0;
}

int main(int argc, char *argv[])
{
    char *portname;
    int fd;

    if (argc != 2) {
        fprintf(stderr, "Usage: %s port\n", argv[0]);
        return -1;
    }
    portname = argv[1];

    printf("Waiting to open \"%s\"...\n", portname);
    while (0 > (fd = open(portname, O_RDWR | O_NOCTTY | /*O_NONBLOCK*/ O_SYNC))) {
        usleep(50000);
    }
    if (fd < 0) {
        fprintf(stderr, "Error opening \"%s\": %s\n", portname, strerror(errno));
        return -1;
    }
    /* Baudrate 115200, 8 bits, no parity, 1 stop bit. */
    if (0 > set_interface_attribs(fd, B115200)) {
        return -1;
    }

    tcsendbreak(fd, 0);
    tcflush(fd, TCIOFLUSH);
    tcsendbreak(fd, 0);
    tcflush(fd, TCIOFLUSH);

    int connected = 0;
    const uint8_t start[4] = { 0xa0, 0x0a, 0x50, 0x05 };
    const uint8_t expected[4] = { 0x5f, 0xf5, 0xaf, 0xfa };
    while (connected == 0) {
        for (int i = 0; i < 4; i++) {
            printf("Send: 0x%02x\n", start[i]);
            int wlen = write(fd, &start[i], 1);
            if (wlen < 0) {
                perror("Error from write()");
                return -1;
            }
            tcdrain(fd);
            uint8_t val;
            int rlen = read(fd, &val, 1);
            if (rlen < 0) {
                perror("Error from read()");
                return -1;
            }
            printf("Recv: 0x%02x\n", val);
            if (val != expected[i]) {
                if (0 > set_interface_attribs(fd, B115200)) {
                    return -1;
                }
                break;
            } else if (i == 3) {
                connected = 1;
            }
        }
    }
}
