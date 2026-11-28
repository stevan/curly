# kind: refused
# perl names its own line: 'a1 at FILE line 5.'
use v5.42;
my $n = 1;
die "a" . $n
    if $n;
