# check: fails: differs from perl
# kind: same
# A run's directory holds what the headers name and nothing else (D282): a
# file another run left, or one of the repository's own, is not there.
use v5.42;
if (open(my $fh, '<', 'Makefile')) {
    say "there";
} else {
    say "not there";
}
