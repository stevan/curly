# kind: refused
# perl globs: the one name it gives is the handle's address (T693).
use v5.42;
my %h;
my $l = <$h{fh}>;
