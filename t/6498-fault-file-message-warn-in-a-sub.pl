# t/models/file.py 6498
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
sub note($text) { warn $text; return; }
open(my $fh, '<', 'in.txt') or die "no\n";
my $l = <$fh>;
say "before";
note("careful");
