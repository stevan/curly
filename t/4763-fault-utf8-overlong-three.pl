# t/models/io.py 4763
# kind: fault
# stdin: ok\n\0340\0200\0200\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
