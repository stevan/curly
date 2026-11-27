# kind: refused
# perl dies: Cannot invoke method "m" on a non-instance.
use v5.42;
use experimental 'class';
class P { method m { 1 } method n { __CLASS__->m } }
