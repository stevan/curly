# kind: refused
# perl runs it (R17-13-attr-repeated): two readers.
use v5.42;
use experimental 'class';
class P { field $x :reader :reader(q); }
