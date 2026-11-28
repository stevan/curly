# A method's signature is a sub's (step 17a): placeholders, `$` alone, and
# `@` and `%` alone for what is left, which name nothing; defaults with
# `=`, `//=` and `||=`; and a slurpy array or hash with a name. The
# breakages of the step showed no test reached a placeholder in a method.
use v5.42;
use experimental 'class';
class P {
    method skip($, $y = 2, @) { $y }
    method rest($x, %) { $x }
    method opts($x //= "d", $z ||= "e") { "$x$z" }
    method all($first, @more) { $first . ":" . scalar(@more) }
    method pairs(%o) { join ",", map { "$_=$o{$_}" } sort keys %o }
}
my $p = P->new;
say $p->skip(1), $p->skip(1, 5, 6, 7), $p->rest(3, a => 1);
say $p->opts, $p->opts(undef, 0), $p->opts("x", "y");
say $p->all(1, 2, 3), " ", $p->pairs(b => 2, a => 1);
