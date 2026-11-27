# kind: refused
# perl dies (R17-01-sub-from-field): Undefined subroutine &P::helper.
use v5.42;
use experimental 'class';
sub helper($n) {
    return "h$n";
}
class P { field $id = helper(2); }
