# kind: refused
# perl runs it: '55' (T346).
use v5.42;
my $x = 1;
my $r = \$x;
sub pair($p, $q) {
    return "$p$q";
}
say(pair($r->$*, ($x = 5)));
