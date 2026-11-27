use v5.42;
use experimental 'class';
sub helper() { "h" } role R { method m { helper() } } class C :does(R) { } say C->new->m;
