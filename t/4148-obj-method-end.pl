# kind: refused
# perl takes it for an END block (R17-02-method-end).
use v5.42;
use experimental 'class';
class P { method END { 1 } }
