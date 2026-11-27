# kind: refused
# perl makes the list's element undef (T9).
use v5.42;
my @a = (1, 2);
for my $x (@a) {
    undef $x;
}
