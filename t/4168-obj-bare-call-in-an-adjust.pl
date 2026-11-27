# kind: refused
# perl dies: Undefined subroutine &P::helper.
use v5.42;
use experimental 'class';
sub helper($n) {
    return "h$n";
}
class P { ADJUST { helper(3) } }
