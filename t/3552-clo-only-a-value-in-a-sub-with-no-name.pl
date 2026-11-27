# kind: refused
# perl warns: Useless use of a constant (2) in void context (it folds 1 + 1).
use v5.42;
my $f = sub {
    1 + 1;
    return 2;
};
