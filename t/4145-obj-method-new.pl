# kind: refused
# perl warns (T409-new): Subroutine new redefined; and new is lost.
use v5.42;
use experimental 'class';
class P { method new { 1 } }
