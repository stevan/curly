# kind: refused
# perl warns here, though of an elsif's whole test it does not.
use v5.42;
my $l;
if (@ARGV) {
    say "args";
} elsif (($l = <STDIN>) && 1) {
    print $l;
}
