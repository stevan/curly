# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $r = [1, 2];
my @a = (1);
say "$r->[$#a]";
