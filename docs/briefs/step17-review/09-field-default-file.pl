use v5.42;
use experimental 'class';
my $y = 5; class P { field $x = $y; field $y = 1; method m { "$x $y" } } say P->new->m;
