# kind: refused
# perl prints to the handle: what shift gives back holds it. Refused all the same: the array that gave the handle is changed.
use v5.42;
open(my $w, '>', 'o.txt') or die "no\n";
my @h = ($w);
print { $h[0] } 'a', ref(shift(@h));
