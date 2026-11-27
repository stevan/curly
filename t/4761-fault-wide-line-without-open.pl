# t/models/io.py 4761
# kind: fault
# stdin: plain\n\0303\0251\n
use v5.42;
my $a1 = <STDIN>;
print $a1;
my $a2 = <STDIN>;
print $a2;
