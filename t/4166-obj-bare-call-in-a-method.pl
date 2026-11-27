# kind: refused
# perl dies (R17-01-sub-from-method): Undefined subroutine &P::helper.
use v5.42;
use experimental 'class';
sub helper($n) {
    return "h$n";
}
class P { method m { helper(1) } }
