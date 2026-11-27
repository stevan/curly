# model: t/models/clo.py
use v5.42;
sub apply($f, @l) {
    return map { $f->($_) } @l;
}
sub compose($f, $g) {
    return sub ($x) { $f->($g->($x)) };
}
{
    say(join(",", apply(sub ($x) { $x * $x }, 1, 2, 3)));
    my $h = compose(sub ($x) { $x + 1 }, sub ($x) { $x * 2 });
    say($h->(5), compose($h, $h)->(1));
    my $by = sub ($p, $q) { $q <=> $p };
    my @s = sort { $by->($a, $b) } (3, 1, 2);
    my $odd = sub ($n) { $n % 2 };
    my @o = grep { $odd->($_) } (1 .. 6);
    say("@s @o");
    my %reg;
    for my $name ("a", "b") {
        my $tag = uc($name);
        $reg{$name} = sub ($v) { "$tag$v" };
    }
    say($reg{a}->(1), $reg{b}->(2));
}
{
    my $boom = sub ($m) { die "$m\n" };
    my $r = "none";
    try {
        $boom->("bang");
    }
    catch ($e) {
        chomp $e;
        $r = $e;
    }
    say($r);
    my $safe = sub ($f) { try { return $f->() } catch ($e) { return "caught" } };
    say($safe->(sub { 5 }), $safe->(sub { die "x\n" }));
    my $code = sub { 1 };
    try {
        die $code;
    }
    catch ($e) {
        say(ref($e), " ", $e == $code ? "same" : "diff", " ", $e->());
    }
}
{
    my @keep;
    for my $i (1 .. 3) {
        my @a = ($i) x $i;
        push @keep, sub { scalar(@a) . ":" . join("", @a) };
    }
    say(join(",", map { $_->() } @keep));
    my $self;
    $self = sub ($n) { return $n ? $self->($n - 1) + 1 : 0 };
    say($self->(4));
}
