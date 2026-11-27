# t/models/io.py 4753
# kind: fault
# env: CURLY_IO_A=a
use v5.42;
say $ENV{CURLY_IO_A};
my $r = \%ENV; $r->{CURLY_IO_A} = "b";
say "not reached";
