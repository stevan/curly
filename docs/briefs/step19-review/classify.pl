# For differential.py (the independent review of step 19): reads a JSON
# list of programs from stdin and writes, for each, "" if perl 5.42
# compiles it in silence, "W: ..." with its first warning, or "D: ..."
# with what it died of. Nothing is run: each program is wrapped in a sub.
# (This file has no `use VERSION` of its own: under v5.42 evalbytes
# refuses, before it reads the program's own `use utf8`, any text with a
# byte past ASCII, and under an older one perl refuses the program's
# `use v5.42`.)
use strict;
use warnings;
use feature 'evalbytes';
use JSON::PP;
binmode(STDIN); binmode(STDOUT);
my $cases = JSON::PP->new->utf8->decode(do { local $/; <STDIN> });
my @out;
for my $text (@$cases) {
    my @w;
    local $SIG{__WARN__} = sub { push @w, $_[0] };
    # (As bytes, so that the program's own `use utf8` reads them, as it
    # does in a file.)
    utf8::encode($text);
    my $ok = evalbytes "my \$f = sub {\n$text\n}; 1";
    my $err = $@;
    push @out, !$ok ? "D: " . (split /\n/, $err)[0] : @w ? "W: " . (split /\n/, $w[0])[0] : "";
}
print JSON::PP->new->utf8->encode(\@out);
