use v5.42;
use experimental 'class';
sub helper($n) { "h$n" } class P { field $id = helper(2); method id { $id } } say P->new->id;
