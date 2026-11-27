use v5.42;
use experimental 'class';
my $x = "file"; class P { method m { $x } field $x = "field"; method n { $x } } my $p = P->new; say $p->m, " ", $p->n;
