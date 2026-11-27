use v5.42;
use experimental 'class';
sub helper($n) { "h$n" } class P { method m { main::helper(1) } } say P->new->m;
