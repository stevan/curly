# kind: refused
# perl closes the file: close $fh || die is close($fh || die).
use v5.42;
open(my $fh, '<', 'in.txt');
close $fh || die "x";
