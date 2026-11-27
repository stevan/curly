# kind: refused
# perl runs it: Q is a class of its own.
use v5.42;
use experimental 'class';
class P { class Q { } }
