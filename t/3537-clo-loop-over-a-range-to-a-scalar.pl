# perl runs it: '12'. D166 refused it; a lone range is no scalar of
# the list's, and D259 takes it in.
use v5.42;
my $n = 2;
my @s;
for my $i (1 .. $n) {
    push @s, sub { $i };
}
say $s[0]->(), $s[1]->();
