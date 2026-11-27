# kind: fault
# perl dies with the message, which ends in a newline: no line added. A dies test would do; the fault is the undef on the left.
use v5.42;
my %h = (a => 1);
my $u;
my $f = $h{a} or die "no\n";
say $f;
my $g = $u + 1 or die "no\n";
