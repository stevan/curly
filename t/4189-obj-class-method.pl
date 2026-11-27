# kind: refused
# perl dies (T411-class): Cannot invoke method "m" on a non-instance.
use v5.42;
use experimental 'class';
class P { method m { 1 } }
P->m;
