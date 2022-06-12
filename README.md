# MediaTek LTE Baseband RE

## Introduction

MediaTek is a fabless semiconductor company that makes, among other
things, smartphone SoCs with built-in LTE modems. These SoCs interest me
for the following reasons:

- They're cheap.
- They're extremely popular.
- They're used in many inexpensive LTE smartphones.
- They primarily use off-the-shelf IP cores, which for the ARM cores means
  documentation is publicly available.
- Their Linux kernel sources are generally available, though not always
  buildable.
- While the BSPs for these SoCs usually support code signing/image
  verification/etc., most phones based on them either don't enable it or
  implement it incorrectly, enabling us to run our own code and build our
  own firmware.
- You can usually find their datasheets, TRMs, register manuals,
  functional specifications, and reference designs leaked online.
- Everyone else is interested in Qualcomm SoCs, so MediaTek SoCs are
  currently low-hanging fruit. :)

The LTE modem in these SoCs consists of two main components:

- A Cortex-R4 to handle the LTE protocol.
- A Coresonic DSP to hande the data-to-RF conversion.

The initial goals of this project are to reverse engineer the Coresonic
DSP, its "SIMT" instruction set, the interface between the Cortex-R4 and
the Coresonic DSP, and the interface between the Cortex-R4 and the SoC's
applications processor. Doing this will empower users to build custom
modems using inexpensive, off-the-shelf Android smartphones. Some examples
of what would be possible:

- Over-engineered walkie-talkie.
- Smartphone DECT handset.
- Cognitive radio in TV whitespace.
- Dongle-free smartphone digital TV receiver.
- Dongle-free smartphone SDR/spectrum analyzer.
- Free Software LTE modem.

This repository will track the notes I write and the tools I build to
do all of this.

## Current Progress

The DSP firmware can be decoded. See the [DSP](DSP) directory for some
scripts to do this and to read the notes on my findings.

My current task list is in [Tasks.md](Tasks.md).

## Additional Information

See the [General-Notes.adoc](General-Notes.adoc) file in this directory
for general information about MediaTek's LTE modems and SoCs.
Information on each subsystem can be found in the "Notes.md" file in the
directory for that subsystem.

The [Documents.md](Documents.md) file contains a list of research papers,
presentations, patents, and other documents that are or might be relevant
to this project.

## Chat

Join us in the `#postmarketos-lowlevel` channel on
[Matrix](https://matrix.to/#/#lowlevel:postmarketos.org) or
[OFTC IRC](https://webchat.oftc.net/?channels=postmarketos-lowlevel)
to discuss this and other low-level smartphone firmware projects.


## License

Except where otherwise stated:

* All software in this repository (e.g., the serial monitor and the scripts
  and tools to build it, tools for unpacking and generating firmware, tools
  for building documentation, etc.) is made available under the
  [GNU General Public License, version 3 or later][gpl].
* All copyrightable content that is not software (e.g., chip register and
  programming manuals, reverse engineering notes, this README file, etc.) is
  licensed under the
  [Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].


[gpl]: COPYING.txt
[cc-by-sa]: https://creativecommons.org/licenses/by-sa/4.0/
