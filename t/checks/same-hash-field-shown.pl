# check: fails: keys without sort
# A hash field whose method prints its keys in perl's order (step 17a).
use v5.42;
use experimental 'class';
class P { field %h = (b => 2, a => 1, c => 3); method show { join ",", keys %h } }
say P->new->show;
