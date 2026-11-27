# t/models/io.py 4751
# kind: fault
# env: CURLY_IO_A=a
use v5.42;
say $ENV{CURLY_IO_A};
delete $ENV{CURLY_IO_A};
say "not reached";
