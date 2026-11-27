# How a sub with no name, `__SUB__` and a call through a reference are
# written, by hand, with perl's answers (step 14): placeholders in a
# signature, an operator that is a word after the sub's block and after
# `__SUB__`, a return in a sub in a map's block, a sub in a loop's list,
# and a call through a reference that gives a list among a call's
# arguments, handed on by a sub too.
use v5.42;
my $skip = sub ($, $y) { $y };
my $rest = sub ($x, @) { $x };
my $none = sub (%) { "none" };
say $skip->(1, 2), $rest->(3, 4, 5), $none->(a => 1);
say((sub { 1 } xor 0) ? "t" : "f", (sub ($x) { $x } xor 1) ? "t" : "f");
my $me = sub { return (__SUB__ and "yes") };
say $me->();
my @fs = map { my $v = $_; sub { return $v * 2 } } (1, 2, 3);
say join(",", map { $_->() } @fs);
my @c;
for my $f (sub { scalar(@c) }, sub { 0 }) {
    push @c, 1;
}
say scalar(@c);
my $two = sub { return (1, 2) };
sub cnt(@l) {
    return scalar(@l);
}
sub pass() {
    return $two->();
}
say cnt($two->(), 3), cnt(pass(), 3), cnt(3, $two->());
