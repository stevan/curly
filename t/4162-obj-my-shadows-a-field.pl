# kind: refused
# perl runs it: the my, in silence.
use v5.42;
use experimental 'class';
class P { field @a; method m { my @a = (1); return scalar(@a) } }
