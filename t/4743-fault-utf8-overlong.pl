# t/models/io.py 4743
# kind: fault
# stdin: ok\n\0300\0201\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
