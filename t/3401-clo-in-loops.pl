# model: t/models/clo.py
use v5.42;
{
    my @s;
    for my $i (1 .. 3) {
        push @s, sub { return $i * 10 };
    }
    say(join(",", map { $_->() } @s));
    my @t;
    for (my $i = 0; $i < 3; $i++) {
        push @t, sub { $i };
    }
    say(join(",", map { $_->() } @t));
    my @u;
    for my $i (1 .. 3) {
        my $j = $i;
        push @u, sub { return $j++ };
    }
    say(join(",", $u[0]->(), $u[0]->(), $u[1]->(), $u[2]->(), $u[0]->()));
    my @w;
    my $n = 0;
    while ($n < 3) {
        my $k = $n++;
        push @w, sub { $k };
    }
    say(join(",", map { $_->() } @w));
    my @q = ("a", "b");
    my @v;
    while (my $e = shift @q) {
        push @v, sub { $e };
    }
    say(join(",", map { $_->() } @v));
}
{
    my @a = (4, 5, 6);
    my @s;
    for my $x (@a) {
        push @s, sub { $x + 1 };
    }
    say(join(",", map { $_->() } @s), " ", scalar(@a), " $a[0]");
    my %h = (a => 1, b => 2);
    my @k;
    for my $key (sort keys %h) {
        push @k, sub { $key };
    }
    delete $h{a};
    $h{c} = 3;
    say(join(",", map { $_->() } @k), " ", join(",", sort keys %h));
    my @g;
    for my $i (1 .. 2) {
        for my $j (1 .. 2) {
            push @g, sub { "$i$j" };
        }
    }
    say(join(",", map { $_->() } @g));
    my @m = map { my $v = $_ * 2; sub { $v } } (1, 2, 3);
    say(join(",", map { $_->() } @m));
}
{
    my $sum = 0;
    my @add;
    for my $i (1 .. 3) {
        push @add, sub { $sum += $i; return $sum };
    }
    say(join(",", $add[2]->(), $add[0]->(), $add[1]->()), " ", $sum);
}
