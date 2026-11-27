# kind: refused
# perl runs it (R17-03-arrow-amp-other) on another object of the class, and dies of another class's.
use v5.42;
use experimental 'class';
class P { my method b { 1 } method a($o) { $o->&b() } }
