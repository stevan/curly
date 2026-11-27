# check: ok
# A hash through a reference where it is copied, counted or tested, as a
# named one is: no order shows (step 13b).
use v5.42;
my $h = {pear => 3, apple => 1, fig => 2};
my %c = %{$h};
my %d = $h->%*;
my $n = keys $h->%*;
if (%{$h}) { say "some"; }
say $n, scalar(keys %c), scalar(keys %d), keys(%{$h}) + 1;
my $r = {x => [{y => 1, z => 2}]};
say scalar($r->{x}[0]->%*), scalar(%{ $r->{x}[0] });
$r->{x}[1]->%* = (a => 1, b => 2);
%{$r->{w}} = (c => 3);
my $y;
($y, %{$r->{v}}) = (1, d => 4);
sub opts($x, %o) { return $x . scalar(%o); }
say opts("n", $r->{x}[1]->%*), scalar(keys %{$r->{v}});
