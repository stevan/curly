# kind: refused
# perl runs it, and says nothing.
use v5.42;
my @s = sort { my $f = sub { $a }; $f->() <=> $b } (2, 1);
