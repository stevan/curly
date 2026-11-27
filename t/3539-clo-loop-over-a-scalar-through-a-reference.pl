# kind: refused
# perl runs it: '9'.
use v5.42;
my $v = 1;
my %h = (s => \$v);
my @s;
for my $x (${ $h{s} }) {
    push @s, sub { $x };
}
