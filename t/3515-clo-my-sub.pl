# kind: refused
# perl dies: Undefined subroutine &main::fact (T369).
use v5.42;
my sub fact($n) {
    return $n <= 1 ? 1 : $n * fact($n - 1);
}
say fact(5);
