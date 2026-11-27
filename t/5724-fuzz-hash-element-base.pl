# kind: refused
# perl prints 'u': the freed hash has no key k.
use v5.42;
my %h = (a => {k => 1});
sub f() {
    %h = (a => {k => 2});
    return "k";
}
say $h{a}{f()} // "u";
