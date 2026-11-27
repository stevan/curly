# scalar without brackets, of an array, a hash and the whole container through a reference (D250).
use v5.42;
my @a = (1, 2, 3);
my %h = (a => 1, b => 2);
my $r = [4, 5];
my $g = {x => 1};
say scalar @a;
say scalar %h;
say scalar keys %h;
say scalar values %h;
say scalar $r->@*;
say scalar @{$r};
say scalar %{$g};
say scalar $g->%*;
say scalar @a == 3 ? "y" : "n";
say join ",", (scalar @a, 9);
my @n = ();
say scalar @n;
sub count($x, @rest) {
    return scalar @rest;
}
say count(1, 2, 3);
my $f = sub { scalar @a };
push @a, 4;
say $f->();
