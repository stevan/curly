# kind: refused
# perl takes \&P::helper, which is no sub.
use v5.42;
use experimental 'class';
sub helper($n) {
    return "h$n";
}
class P { method m { return \&helper } }
