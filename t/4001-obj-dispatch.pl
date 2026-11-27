# model: t/models/obj.py
use v5.42;
use experimental 'class';
my @said;
class Shape {
    field $name :param :reader = "shape";
    method area { 0 }
    method describe { $name . " " . $self->area }
    method kind { __CLASS__ }
    method twin { __CLASS__->new(name => "twin of $name") }
    ADJUST { $self->hello }
    method hello { push @said, "Shape.hello"; return }
}
class Square :isa(Shape) {
    field $side :param :reader = 1;
    method area { $side * $side }
    method hello { return }
}
class Cube :isa(Square) {
    method area { 6 * $self->SUPER::area() }
    method label { "cube:" . $self->SUPER::describe() }
}
class Counter {
    field $n = 0;
    my method bump($by) { $n += $by; return $n }
    method add2 { $self->&bump(1); return $self->&bump(1) }
    method parts { return ($n, $n + 1, $n + 2) }
    method one { return $n }
}
my @shapes = (Shape->new, Square->new(name => "sq", side => 3), Cube->new(name => "cu", side => 2));
say join "|", map { $_->describe } @shapes;
say join "|", map { $_->kind } @shapes;
say join "|", map { ref $_->twin } @shapes;
say $shapes[2]->twin->name;
say $shapes[2]->label;
my $t = Shape->new->twin;
say scalar(@said);
say join ",", map { ($_ isa Shape ? 1 : 0) . ($_ isa Square ? 1 : 0) . ($_ isa Cube ? 1 : 0) } @shapes;
say join ",", map { ref $_ } @shapes;
say blessed($shapes[1]), " ", reftype($shapes[1]);
my $z = 1;
my $first = $shapes[0];
say defined(blessed([1])) ? "b" : "u", reftype([1]), reftype({}), reftype(\$z), reftype(\$first), defined(reftype(1)) ? "r" : "u";
my $k = Counter->new;
say $k->add2, $k->add2;
my @p = $k->parts;
say "@p";
say $k->one + 1;
say((Counter->new isa Shape) ? "yes" : "no");
say(((undef) isa Shape) ? "yes" : "no", ("Shape" isa Shape) ? "yes" : "no", ([] isa Shape) ? "yes" : "no");
