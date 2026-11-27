use v5.42;
say "a";
use experimental "class";
class P { method m { 1 } }
say P->new->m;
