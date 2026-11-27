# A call through a reference among a call's arguments, which stores to an
# argument before it (step 14; D73, D163): the argument is a place, read
# when the sub copies it, as perl reads it. (Where any sub with no name
# gives a list, the arguments are one list, and this is refused: t/3404's
# file has one, and so the line is here.)
use v5.42;
my $y = 1;
my $bump = sub { $y = 9; return 0 };
sub pair($p, $q) {
    return "$p$q";
}
say pair($y, $bump->());
