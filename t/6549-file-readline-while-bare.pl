# kind: refused
# perl stores each line in its global $_ (T511).
use v5.42;
open(my $fh, '<', 'in.txt');
while (<$fh>) {
    say "line";
}
