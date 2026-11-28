# kind: refused
# perl tests the line with defined.
use v5.42;
my $l;
for (my $i = 0; 1 && ($l = <STDIN>); $i++) {
    print $l;
}
