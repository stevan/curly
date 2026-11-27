# kind: refused
# perl dies (R17-10-super-other-invocant): Can't locate object method "m" via package "C".
use v5.42;
use experimental 'class';
class A { method m { 1 } }
class C { method go($o) { $o->SUPER::m } }
