# kind: refused
# perl runs it where the block stands (T408): a method that reads it before then sees undef.
use v5.42;
use experimental 'class';
class P { my $c = 10; }
