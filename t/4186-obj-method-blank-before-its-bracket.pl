# kind: refused
# perl runs it (17-call-forms): the brackets are the arguments.
use v5.42;
use experimental 'class';
class P { method m($x) { $x } }
my $x = P->new->m (1);
