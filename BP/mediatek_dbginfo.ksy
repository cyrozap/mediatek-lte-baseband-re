meta:
  id: mediatek_dbginfo
  endian: le
  title: MediaTek Modem Debug Info
  license: CC0-1.0
seq:
  - id: header
    type: header
  - id: symbols
    type: symbols
    size: header.file_associations_start - header.header_len - 1
  - id: junk
    size: 1
  - id: file_associations
    type: file_associations
    size: _io.size - header.file_associations_start - 1
types:
  header:
    seq:
      - id: magic
        type: str
        size: 4
        encoding: ASCII
      - id: ver
        type: u4
      - id: unk
        type: u4
      - id: version
        type: strz
        encoding: ASCII
      - id: sub
        type: strz
        encoding: ASCII
      - id: build
        type: strz
        encoding: ASCII
      - id: time
        type: strz
        encoding: ASCII
      - id: header_len
        type: u4
      - id: file_associations_start
        type: u4
  symbols:
    seq:
      - id: symbol
        type: symbol
        repeat: eos
  symbol:
    seq:
      - id: name
        type: strz
        encoding: ASCII
      - id: start
        type: u4
      - id: end
        type: u4
  file_associations:
    seq:
      - id: file_association
        type: file_association
        repeat: eos
  file_association:
    seq:
      - id: file
        type: strz
        encoding: UTF-8
      - id: range_count
        type: u4
      - id: symbol_range
        type: symbol_range
        repeat: expr
        repeat-expr: range_count
  symbol_range:
    seq:
      - id: start
        type: u4
      - id: end
        type: u4
