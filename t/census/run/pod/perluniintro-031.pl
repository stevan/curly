use v5.42;
# this prints  c4 80  for the UTF-8 bytes 0xc4 0x80
print join(" ", unpack("U0(H2)*", pack("U", 0x100))), "\n";
