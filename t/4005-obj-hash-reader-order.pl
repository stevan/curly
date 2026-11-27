# kind: new
# D27 through a reader (step 17a; the review of step 17, finding 17): a
# hash field's reader gives its keys and values in the order the keys were
# first stored, as the hash does where it stands. perl's order is another
# every run, so perl is not asked, and the answers are by hand.
use v5.42;
use experimental 'class';
class Bag {
    field %h :reader = (pear => 1, apple => 2, fig => 3);
    method put($k, $v) { $h{$k} = $v; return }
    method drop($k) { delete $h{$k}; return }
}
my $b1 = Bag->new;
say join ",", $b1->h;
$b1->put("apple", 9);
$b1->put("kiwi", 4);
say join ",", $b1->h;
$b1->drop("pear");
$b1->put("pear", 5);
my %c = $b1->h;
say join ",", keys %c;
