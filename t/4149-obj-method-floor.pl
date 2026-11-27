# kind: refused
# perl warns (R17-02-method-floor-ceil): Prototype mismatch, Subroutine floor redefined; the method is never installed.
use v5.42;
use experimental 'class';
class P { method floor { 1 } }
