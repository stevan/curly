# kind: refused
# perl dies: Undefined subroutine &P::helper, when the closure runs.
use v5.42;
use experimental 'class';
sub helper($n) {
    return "h$n";
}
class P { method m { return sub { helper(4) } } }
