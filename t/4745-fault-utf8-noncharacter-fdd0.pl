# t/models/io.py 4745
# kind: fault
# stdin: ok\n\0357\0267\0220\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
