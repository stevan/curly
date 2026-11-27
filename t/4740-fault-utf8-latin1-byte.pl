# t/models/io.py 4740
# kind: fault
# stdin: ok\n\0351\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
