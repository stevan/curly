use v5.42;
use experimental 'class';
sub helper($n) { "h$n" } class P { method m { try { helper(1) } catch ($e) { "caught" } } } say P->new->m;
