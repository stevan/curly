# kind: fault
# perl reverses $_ for a list with nothing in it (T672): 'cba', where $_ is abc.
use v5.42;
for my $w ("abc") {
    my @e;
    say "[", scalar reverse(@e), "]";
}
