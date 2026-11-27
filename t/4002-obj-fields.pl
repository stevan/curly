# model: t/models/obj.py
use v5.42;
use experimental 'class';
class Bag {
    field @items;
    field %count;
    field $last = "none";
    method add(@new) { for my $x (@new) { push @items, $x; $count{$x}++; $last = $x } return scalar(@items) }
    method items_ref { \@items }
    method last_ref { \$last }
    method last { $last }
    method counts { join ",", map { "$_=$count{$_}" } sort keys %count }
    method watcher { sub { $last } }
    method setter { sub ($v) { $last = $v; return } }
    method self_getter { sub { $self->last } }
    method plain { sub { 42 } }
}
class Lazy {
    field $n = 1;
    field $get = sub { $n };
    field $cb;
    ADJUST { $cb = sub { $n * 10 } }
    method bump { $n++; return }
    method both { $get->() . "/" . $cb->() }
}
my $g = Bag->new;
say $g->add("x", "y", "x");
say $g->counts, " ", $g->last;
push $g->items_ref->@*, "z";
say join ",", $g->items_ref->@*;
${ $g->last_ref } = "set";
say $g->last;
say $g->last_ref == $g->last_ref ? "same" : "diff";
my $h = Bag->new;
say $g->last_ref == $h->last_ref ? "same" : "diff";
my $w = $g->watcher;
my $s = $g->setter;
$g->add("q");
say $w->();
$s->("from closure");
say $g->last, " ", $h->last;
say $g->self_getter->();
say $g->plain == $g->plain ? "same" : "diff", $g->watcher == $g->watcher ? "same" : "diff";
my $z = Lazy->new;
say $z->both;
$z->bump;
say $z->both;
