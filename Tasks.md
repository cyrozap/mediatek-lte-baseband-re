# Tasks

- [ ] Load and execute arbitrary code on Cortex-R4.
- [ ] Load and execute code on DSP.
- [ ] Enable debugging on Cortex-R4 (hard).
- [ ] Enable debugging on DSP (also hard).

## Priorities

The primary goal is to be able to control and observe the DSP state. In a
nutshell, this means we need to find ways to load and execute arbitrary code
on the DSP and to read and write its memory and registers.

To do that, we first need to get execution inside the Cortex-R4 because it
has full control over the DSP. There may be a way to control the DSP
entirely from the AP, but if that's possible I'm not sure how to do it.

Ideally, we want to also enable JTAG/SWD debugging on the CR4 and the DSP so
we can get more control over them without any interference from the AP.
Unfortunately, I have yet to find any "enable JTAG interface"-type register
writes in either the modem code or the kernel driver.
