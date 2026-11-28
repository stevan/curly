# kind: refused
# perl prints 1: $_ is matched, the answer raised, and that number is the pattern (T561). The compiler printed 0.
use v5.42;
for ("a") {
    say "1" =~ /a/ ** 2;
}
