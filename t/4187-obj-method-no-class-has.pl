# kind: refused
# perl dies when the call is made (17-missing): Can't locate object method "nope" via package "P".
use v5.42;
use experimental 'class';
class P { }
P->new->nope;
