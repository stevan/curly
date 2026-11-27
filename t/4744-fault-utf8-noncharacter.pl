# t/models/io.py 4744
# kind: fault
# stdin: ok\n\0357\0277\0277\n
use v5.42;
use open ':std', ':encoding(UTF-8)';
my $first = <STDIN>;
print $first;
my $second = <STDIN>;
say "not reached";
