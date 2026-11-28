# perl cuts the array to one element. 13b refused it; D251 takes it in.
use v5.42;
my $r = [1, 2];
$r->$#* = 0;
say scalar $r->@*;
