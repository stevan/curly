# kind: refused
# perl tests the line with defined (T501).
use v5.42;
open(my $fh, '<', 'in.txt');
for (my $i = 0; my $l = <$fh>; $i++) {
    say $i;
}
