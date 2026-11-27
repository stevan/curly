use v5.42;
use experimental 'class';
class P { field $a = do { say "fieldA"; 1 }; field $x :param = 1; ADJUST { say "adjust" } } P->new("x");
