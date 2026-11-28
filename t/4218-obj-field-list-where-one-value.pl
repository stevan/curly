# kind: refused
# perl gives the last value, and warns (17-field-list-scalar): Useless use of a constant in void context.
use v5.42;
use experimental 'class';
class P { field $x = (4, 5, 6); }
