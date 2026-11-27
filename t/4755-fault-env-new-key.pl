# t/models/io.py 4755
# kind: fault
# env: CURLY_IO_A=a
use v5.42;
say $ENV{CURLY_IO_A};
$ENV{CURLY_IO_NEW} .= "x";
say "not reached";
