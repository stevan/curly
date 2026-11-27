# t/models/io.py 4764
# kind: fault
# stdin: ok\n\0365\0200\0200\0200\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
