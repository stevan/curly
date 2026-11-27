use v5.42;
use experimental 'class';
class P { field $a = do { say "fieldA"; 1 }; field $x :param; field $b = do { say "fieldB"; 1 }; ADJUST { say "adjust" } } P->new(y => 1, x => 2);
