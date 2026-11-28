# kind: refused
# perl folds the 1 away and tests the line with defined: a last line 0 is read (T520).
use v5.42;
my $l;
while (1 && ($l = <STDIN>)) {
    print $l;
}
