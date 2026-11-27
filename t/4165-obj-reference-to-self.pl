# kind: refused
# perl runs it (R17-11-sref-self): a store through the reference replaces the object.
use v5.42;
use experimental 'class';
class P { method m { my $r = \$self; return $r } }
