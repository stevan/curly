# t/models/file.py 6490
# kind: fault
# file: bad.txt=ok\nx\0351y\n
use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
open(my $fh, '<', 'bad.txt') or die "no\n";
my $l = <$fh>;
print $l;
$l = <$fh>;
