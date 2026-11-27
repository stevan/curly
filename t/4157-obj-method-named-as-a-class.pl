# kind: refused
# perl calls the method for the class's name below it (R17-04-method-hides-class).
use v5.42;
use experimental 'class';
class Q { }
class P { method Q { 1 } }
