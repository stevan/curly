use v5.42;
printf("%#02x ", $_) for unpack("W*", pack("L", 0x12345678));
