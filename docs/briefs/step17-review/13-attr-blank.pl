use v5.42;
use experimental 'class';
class P { field $x :param (y) = 1; method get { $x } } say P->new(y => 7)->get;
