# t/models/io.py 4759
# kind: fault
# stdin: only\n
use v5.42;
my $a1 = <STDIN>;
print $a1;
my $a2 = <STDIN>;
print $a2;
