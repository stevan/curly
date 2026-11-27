# kind: refused
# perl runs it: 'a'.
use v5.42;
my $s = "ab";
if ($s =~ /a/) {
    say $&;
}
