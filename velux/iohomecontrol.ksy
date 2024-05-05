meta:
  id: iohc
  endian: be
seq:
  - id: sfd
    contents: [0xFF, 0x33]
  - id: control1
    type: control1
  - id: control2
    type: control2
  - id: target_id
    type: b24
  - id: source_id
    type: b24
  - id: command
    type: u1
    enum: command
  - id: payload
    size: control1.payload_length - 16
  - id: counter
    type: u2
  - id: mac
    size: 6
  - id: crc16
    type: u2le

types:
  control1:
    seq:
    - id: order
      type: b2
      enum: order    
    - id: mode
      type: b1
      enum: mode
    - id: payload_length
      type: b5
  control2:
    doc: Extended Frame Information
    seq:
    - id: use_beacon
      type: b1
    - id: routed
      type: b1
    - id: low_power_mode
      type: b1
    - id: ack
      type: b1
    - id: unknown
      type: b2
    - id: protocol_version
      type: b2

enums:
  order:
    0: single
    1: next_in_series
    2: next_in_parallel 
    3: command_group_end
  mode:
    0: two_way
    1: one_way
  command:
    0: execute_function
