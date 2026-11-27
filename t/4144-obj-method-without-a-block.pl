# kind: refused
# perl runs it (T419), and the call dies: Undefined subroutine &P::m.
use v5.42;
use experimental 'class';
class P { method m; }
