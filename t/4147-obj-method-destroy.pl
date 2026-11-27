# kind: refused
# perl runs it (T416-destroy) as the object goes.
use v5.42;
use experimental 'class';
class P { method DESTROY { 1 } }
