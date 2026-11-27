# kind: refused
# perl runs it: 'a' (T554).
use v5.42;
my $s = "ab";
if ($s =~ /(a)/) {
    say $1;
}
