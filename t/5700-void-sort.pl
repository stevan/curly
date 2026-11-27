# By hand, with perl's answers (make oracle): a sub called for nothing
# that gives back a sort (D245, T601). perl works the sort's list out and
# skips the sort, so its block never runs; called for a list, it sorts.
use v5.42;
sub p($x) { say "p$x"; return $x }
sub direct() { return sort { say "cmp"; $a <=> $b } (p(2), p(1)); }
sub last_statement() { sort { say "cmp"; $a <=> $b } (2, 1) }
sub branch($c) { return $c ? (sort { say "cmp"; $a <=> $b } (2, 1)) : (0); }
sub right($c) { return $c || sort { say "cmp"; $a <=> $b } (2, 1); }
sub item() { return (1, sort { say "cmp"; $a <=> $b } (2, 1)); }
sub plus() { return +(sort { say "cmp"; $a <=> $b } (2, 1)); }
sub bare() { return sort 3, 1, 2; }
sub hands() { return direct(); }
my $anon = sub { sort { say "cmp"; $a <=> $b } (2, 1) };
direct();
last_statement();
branch(1);
right(0);
item();
plus();
bare();
hands();
$anon->();
say "for nothing: done";
my @l = direct();
say "@l";
@l = branch(1);
say "@l";
@l = hands();
say "@l";
say join(",", bare(), item(), $anon->());
direct() for 1 .. 2;
say "end";
