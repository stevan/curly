# env: CURLY_GC_STRESS=0 CURLY_GC_POISON=0 CURLY_HEAP_CAP=8388608
# A hundred thousand pairs of objects that hold each other, and closures
# that hold their objects, dropped as they are made, under a cap of 8 MB
# (D65, D26, step 17a): the program ends only if an instance nothing
# reaches is freed, cycles and all.
use v5.42;
use experimental 'class';
class Node {
    field $peer :reader :writer;
    field @kids;
    field $v :param :reader;
    method keep($o) { push @kids, $o; return scalar(@kids) }
    method later { sub { $v + scalar(@kids) } }
}
my $n = 0;
for my $i (1 .. 100000) {
    my $a1 = Node->new(v => $i);
    my $a2 = Node->new(v => 1);
    $a1->set_peer($a2);
    $a2->set_peer($a1);
    $a1->keep($a1);
    my $f = $a1->later;
    $a2->keep($f);
    $n += $f->() == $i + 1 && $a2->peer->v == $i ? 0 : 1;
}
say $n;
