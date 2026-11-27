# t/models/io.py 4748
# kind: fault
# stdin: ok\nab\0351cd\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
