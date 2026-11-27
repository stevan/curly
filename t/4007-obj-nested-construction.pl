# Construction inside construction (step 17a; the review of step 17,
# finding 17): each object's default makes the next, five hundred deep,
# every frame counting against D68's limit, under a collection at every
# allocation with each instance in a slot while its fields are made.
use v5.42;
use experimental 'class';
no warnings 'recursion';
class N {
    field $d :param :reader;
    field @pad = (1 .. 3);
    field $kid :reader = $d < 500 ? N->new(d => $d + 1) : undef;
    ADJUST { push @pad, $d }
    method depth { defined $kid ? 1 + $kid->depth : 0 }
    method sum { $pad[3] + (defined $kid ? $kid->sum : 0) }
}
my $n = N->new(d => 0);
say $n->depth, " ", $n->sum, " ", $n->kid->kid->d;
