# kind: refused
# perl prints 1 (T561). The compiler printed 0.
use v5.42;
my $s = "ab";
for ("a") {
    say $s !~ m{a} ** 2;
}
