# kind: refused
# perl names its own line: the format's newline is not its last character.
use v5.42;
my $n = 1;
die sprintf("has\n%d", $n)
    if $n;
