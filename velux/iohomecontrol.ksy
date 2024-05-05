meta:
  id: iohc
  endian: le
seq:
  - id: sfd
    contents: [0xFF, 0x33]
  - id: control1
    type: u1
  - id: control2
    type: u1

instances:
  order:
    value: (control1 & 0b11000000) >> 6
    enum: order    
  mode:
    value: (control1 & 0b00100000) >> 5
    enum: mode
  payload_length:
    value:  control1 & 0b00011111
  use_beacon:
    value: (control2 & 0b10000000) >> 7
  routed:
    value: (control2 & 0b01000000) >> 6
  low_power_mode:
    value: (control2 & 0b00100000) >> 5
  ack:
    value: (control2 & 0b00010000) >> 4
  protocol_version:
    value: control2 & 0b00000011

enums:
  order:
    0: single
    1: next_in_series
    2: next_in_parallel 
    3: command_group_end
  mode:
    0: two_way
    1: one_way