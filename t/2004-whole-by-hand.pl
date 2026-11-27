# By hand, with perl's answers (make oracle): the orders of making, and
# what perl does not do through a reference that it does by name.
use v5.42;
# push and unshift make the array before their list is worked out (T248).
my $r;
push $r->@*, defined($r) ? "made" : "not";
my $u;
unshift @{$u}, ref($u);
say $r->[0], " ", $u->[0];
# An assignment to the whole works its right side out first.
my $s;
$s->@* = (defined($s) ? "made" : "not");
my $h;
%{$h} = (k => ref($h) eq "HASH" ? "made" : "not");
say $s->[0], " ", $h->{k};
# A slice on the left: the right side, the indexes, then the container.
my $t;
my $i = 0;
$t->@[$i, $i + 1] = (defined($t) ? "made" : "not", "b");
say join(",", $t->@*);
# Sorted into itself through a reference, nothing is dropped (T341): it
# is a copy, where `@a = sort ... @a` sorts in place.
my $q = [3];
$q->[3] = 1;
$q->@* = sort { ($a // 0) <=> ($b // 0) } $q->@*;
say join(",", map { $_ // "u" } $q->@*);
my @a = (3);
$a[3] = 1;
my $ra = \@a;
@a = sort { ($a // 0) <=> ($b // 0) } $ra->@*;
say join(",", map { $_ // "u" } @a);
my @b = (2);
$b[2] = 1;
my $rb = \@b;
$rb->@* = sort { ($a // 0) <=> ($b // 0) } @b;
say join(",", map { $_ // "u" } @b);
# A copy is shallow: the references in it are the same ones.
my $grid = [[1], [2]];
my @rows = $grid->@*;
push $rows[0]->@*, 9;
say join(",", $grid->[0]->@*), " ", scalar(@rows);
# An array pushed onto itself takes what it held.
my $c = [1, 2];
push $c->@*, $c->@*;
say join(",", $c->@*);
# The count, where one value is wanted, in each place it may stand.
my $l = [5, 6, 7];
my $n = $l->@*;
my %by;
$by{$l->@*} = "three";
say $n, " ", $by{3}, " ", $l->@* x 2, " ", "n" . $l->$#*, " ", (scalar(@{$l}) == 3 ? "yes" : "no");
# Brackets round the head, a call, and a new array or hash at the head.
sub pair() {
    return [7, 8];
}
say join(",", ($l)->@*, pair()->@*, [1, 2]->@[1], sort keys %{ +{z => 1, y => 2} });
