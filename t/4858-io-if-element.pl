# kind: refused
# perl warns of an element assigned a line too.
use v5.42;
my @a;
if ($a[0] = <STDIN>) {
    print $a[0];
}
