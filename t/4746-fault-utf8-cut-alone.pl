# t/models/io.py 4746
# kind: fault
# stdin: ok\n\0303
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
