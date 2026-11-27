# kind: refused
# perl dies: Can't use string ("1") as an ARRAY ref while "strict refs" in use
use v5.42;
my $r = [1];
say "@{$r->@*}";
