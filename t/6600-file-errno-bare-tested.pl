# kind: refused
# perl tests the number of the error.
use v5.42;
open(my $fh, '<', 'nope.txt');
if ($!) {
    say 'failed';
}
