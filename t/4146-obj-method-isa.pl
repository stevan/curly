# kind: refused
# perl runs it (T416-own): the class's own isa wins over UNIVERSAL's.
use v5.42;
use experimental 'class';
class P { method isa($c) { 1 } }
