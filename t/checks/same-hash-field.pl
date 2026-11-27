# check: ok
# A hash field, declared and filled, read only by its keys sorted (step
# 17a).
use v5.42;
use experimental 'class';
class P { field %h = (b => 2, a => 1); method keys_ { join ",", sort keys %h } method count { scalar(keys %h) } method m(%o) { scalar(keys %o) } method keys { "k" } }
say P->new->keys_, P->new->count, P->new->m(x => 1), P->new->keys;
