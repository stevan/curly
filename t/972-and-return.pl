# perl prints t (T139); a statement joined to return, since D260.
use v5.42;
sub f($c) {
    $c and return "t";
    return "f";
}
say f(1);
