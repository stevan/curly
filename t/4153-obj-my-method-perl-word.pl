# kind: refused
# perl takes it for every join below it (R17-03-my-method-join).
use v5.42;
use experimental 'class';
class P { my method join { 1 } }
