# kind: refused
# perl dies (R17-03-lexical-before-declared): Undefined subroutine &P::b.
use v5.42;
use experimental 'class';
class P { method a { $self->&b() } my method b { 1 } }
