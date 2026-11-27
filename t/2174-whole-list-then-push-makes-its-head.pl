# kind: refused
# perl runs it: 'd' (the list holds $h itself, which the push made a hash).
use v5.42;
my $h;
my @l = ($h, push($h->{m}->@*, 1));
say defined $l[0] ? "d" : "u";
