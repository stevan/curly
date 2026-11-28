# t/models/file.py 6489
# kind: fault
use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
open(my $out, '>', 'o.txt') or die "no\n";
print $out "é\n";
say "before";
print $out chr(0xFFFE);
