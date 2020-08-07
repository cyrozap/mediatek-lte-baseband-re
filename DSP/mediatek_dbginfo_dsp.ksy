meta:
  id: mediatek_dbginfo_dsp
  endian: le
  title: MediaTek Debug Info for DSP
  license: CC0-1.0
seq:
  - id: magic
    contents: "CATICTNR"
  - id: ver
    type: u4
  - id: footer_offset
    type: u4
instances:
  footer:
    pos: footer_offset
    type: footer
types:
  dbginfo:
    seq:
      - id: header
        type: header
    instances:
      symbols:
        pos: _parent.offset + header.symbols_start
        type: symbols
        size: header.file_associations_start - header.symbols_start - 1
      file_associations:
        pos: _parent.offset + header.file_associations_start
        type: file_associations
        # size: _parent.len - 16 - header.file_associations_start - 1
    types:
      header:
        seq:
          - id: magic
            contents: "CATI"
          - id: ver
            type: u4
          - id: unk
            type: u4
          - id: version
            type: strz
            encoding: "ASCII"
          - id: platform
            type: strz
            encoding: "ASCII"
          - id: build_name
            type: strz
            encoding: "ASCII"
          - id: build_time
            type: strz
            encoding: "ASCII"
          - id: symbols_start
            type: u4
          - id: file_associations_start
            type: u4
      symbols:
        seq:
          - id: symbol
            type: symbol
            repeat: eos
        types:
          symbol:
            seq:
              - id: name
                type: strz
                encoding: "ASCII"
              - id: start
                type: u4
              - id: end
                type: u4
      file_associations:
        seq:
          - id: file_association
            type: file_association
            repeat: expr
            repeat-expr: 30  # Arbitrary limit because the array of file associations is null-terminated and Kaitai Struct doesn't have any "repeat until null" functionality.
        types:
          file_association:
            seq:
              - id: file
                type: strz
                encoding: "UTF-8"
              - id: range_count
                type: u4
              - id: symbol_range
                type:
                  switch-on: _parent._parent.header.ver
                  cases:
                    1: symbol_range_v1
                    2: symbol_range_v2
                repeat: expr
                repeat-expr: range_count
            types:
              symbol_range_v1:
                seq:
                  - id: start
                    type: u4
                  - id: end
                    type: u4
              symbol_range_v2:
                seq:
                  - id: start
                    type: u4
                  - id: end
                    type: u4
                  - id: unk3
                    type: u4
  footer:
    seq:
      - id: section_count
        type: u4
      - id: sections
        type: section
        repeat: expr
        repeat-expr: section_count
    types:
      section:
        seq:
          - id: offset
            type: u4
          - id: name
            type: strz
            encoding: "ASCII"
          - id: unk3
            type: strz
            encoding: "ASCII"
        instances:
          dbginfo:
            io: _root._io
            pos: offset
            type: dbginfo
