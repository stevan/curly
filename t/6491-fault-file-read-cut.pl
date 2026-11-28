# t/models/file.py 6491
# kind: fault
# file: cut.txt=ok\na\0303
use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
open(my $fh, '<', 'cut.txt') or die "no\n";
my @l = <$fh>;
