# USB download mode handshake tool

The `handshake` utility waits for the selected serial port to appear,
then immediately connects to it and tries to send a handshake sequence.
Because this is a timing-sensitive operation, and because the port setup
requires particular TTY settings, this program is written in C instead
of Python.

```
Usage: ./handshake port
```
