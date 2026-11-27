use v5.42;
print unpack( '%32A*', "\x01\x10" ), "\n";  # prints 17
