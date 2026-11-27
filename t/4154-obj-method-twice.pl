# kind: refused
# perl warns (T409): Method m redefined, and takes the last.
use v5.42;
use experimental 'class';
class P { method m { 1 } method m { 2 } }
