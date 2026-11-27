# kind: refused
# perl's subs share the scalar: '9,2' (T371).
use v5.42;
my $n = 1;
my @s;
for my $i ($n, 2) {
    push @s, sub { $i };
}
