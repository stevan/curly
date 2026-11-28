# kind: refused
# perl warns: Value of <HANDLE> construct can be "0" (T693).
use v5.42;
open(my $fh, '<', 'in.txt');
if (my $l = <$fh>) {
    print $l;
}
