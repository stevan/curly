# kind: refused
# perl runs it: a class may be declared in a block.
use v5.42;
use experimental 'class';
{
    class P { }
}
