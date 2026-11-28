# A method that gives a list, handed on (step 17a; D18, D172): among a
# call's arguments, where the arguments are built as one list; by a sub
# that returns it, and by a method that returns another's, each a list
# where a list is wanted; a method of one name in two classes, the one
# that gives a list and the one that gives one value. The breakages of the
# step showed no test reached a method's list handed on.
use v5.42;
use experimental 'class';
sub count(@l) { scalar(@l) }
sub parts_of($o) { return $o->parts }
class A {
    method parts { return (1, 2, 3) }
    method more { return $self->parts }
    method v { return (7, 8) }
}
class B {
    method v { return 9 }
}
my $a1 = A->new;
say count(1, $a1->parts), count($a1->more), count(parts_of($a1), 5);
my @l = parts_of($a1);
my @m = $a1->more;
say "@l|@m";
my @v = map { $_->v } (A->new, B->new);
say "@v";
say count(B->new->v, 1), count(A->new->v, 1);
