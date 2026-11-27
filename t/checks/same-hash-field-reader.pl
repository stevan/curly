# check: fails: a reader of a hash field
# A hash field with a reader, whose pairs come out in perl's order
# (step 17a).
use v5.42;
use experimental 'class';
class P { field %h :reader = (b => 2, a => 1, c => 3); }
my %c = P->new->h;
say join ",", sort keys %c;
