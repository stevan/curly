# kind: fault
# A sub called for nothing that gives back `(LIST) x N` (D245): perl
# repeats one value then, the list worked out for one value.
use v5.42;
my $g = sub { return (1, 2) x 2 };
say join(",", $g->());
$g->();
say "not reached";
