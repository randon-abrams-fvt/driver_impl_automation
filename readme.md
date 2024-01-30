# DBC File Setup

## DBC parameters

### Network name

- The name of the first network will be used as the name for the driver object

## Message Parameters

### Message name

- The name of the message will be used as the name for the message object

### CG_MessageInstName Attribute

- This message attribute value will be used as the name for the instantiated message variable

### CG_RX_TX Attribute

- This is used to determine if the message is a TX or RX message. If it is set to none, the message will be ignored by the script

## Signals Parameters

### Signal name

- Used for the signal name within the message data struct

### CG_VarType Attribute

- This signal attribute along with the signal byte order, bit length, and bit position will be used to assign a fixed endian type

## Running Exe

The exe is in the dist folder

dbc_to_driver.exe `<path-to-dbc-file>`
