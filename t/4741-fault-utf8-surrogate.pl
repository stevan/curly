# t/models/io.py 4741
# kind: fault
# stdin: ok\n\0355\0240\0200\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
