# kind: refused
# perl runs it (T411-sub): a sub called as a method, with the class's name or an object first.
use v5.42;
use experimental 'class';
class P { sub make() { 1 } }
