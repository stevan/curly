# kind: refused
# perl runs it (R17-03-arrow-amp-public) with no dispatch: P.b where dispatch gives Q.b.
use v5.42;
use experimental 'class';
class P { method a { $self->&b() } method b { 1 } }
