meta:
  id: mt8183_pcm_allinone
  endian: le
  title: MediaTek MT8183 PCM All-in-One Binary
  license: CC0-1.0
doc: "https://github.com/coreboot/coreboot/blob/a90854d429c5775d51021fbd488c9a2af153f250/src/soc/mediatek/mt8183/spm.c#L220-L226"
seq:
  - id: firmware_size
    type: u2
  - id: binary
    size: 4 * firmware_size
  - id: descriptor
    type: pcm_desc
  - id: version
    type: strz
    encoding: ASCII
types:
  pcm_desc:
    seq:
      - id: size
        type: u2
      - id: sess
        type: u1
      - id: replace
        type: u1
      - id: addr_2nd
        type: u2
      - id: reserved
        type: u2
      - id: vector
        type: u4
        repeat: expr
        repeat-expr: 16
