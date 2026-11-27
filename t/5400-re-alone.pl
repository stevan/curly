# kind: refused
# perl runs it: '1' if $_ matches.
use v5.42;
for ("a") {
    say /a/ ? 1 : 0;
}
