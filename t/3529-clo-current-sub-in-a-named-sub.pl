# kind: refused
# perl runs it: '120'.
use v5.42;
sub fact($n) {
    return $n <= 1 ? 1 : $n * __SUB__->($n - 1);
}
say fact(5);
