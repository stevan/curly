# kind: refused
# perl runs it (R17-09-param-shadows-field): the parameter, in silence.
use v5.42;
use experimental 'class';
class P { field $x = 1; method m($x) { $x } }
