# By hand, with perl's answers (step 13c): the orders of a store through a
# scalar through a reference (T344's, for a scalar: `=` works its right
# side out first, the others make the scalar first); a scalar variable
# whose reference is taken read late, as any variable is (D14, T346: `$x
# + ($$r = 5)` is 10); chomp and chop of one; a default; a file's
# variable stepped by a sub; references taken in a map.
use v5.42;
my $r;
${ $r } = defined($r) ? "made" : "not";
my $s;
${ $s } .= defined($s) ? "made" : "not";
my $t;
$t->$* //= defined($t) ? "made" : "not";
my $u;
${ $u } += defined($u) ? 1 : 2;
say($r->$*, " ", $s->$*, " ", $t->$*, " ", $u->$*);
my $h = {};
${ $h->{a} } = exists($h->{a}) ? "made" : "not";
${ $h->{b} } .= exists($h->{b}) ? "made" : "not";
say(${ $h->{a} }, " ", ${ $h->{b} });
my $x = 1;
my $rx = \$x;
sub pair($p, $q) {
    return "$p$q";
}
say($x + ($rx->$* = 5), " ", pair($x, (${ $rx } = 6)), " ", $x);
my $line = "a\n";
my $rl = \$line;
chomp($line);
say($rl->$*, "|");
chop($line);
say("[", ${ $rl }, "]");
sub d($p = 5) {
    my $rp = \$p;
    $rp->$*++;
    return $p;
}
say(d(), d(1));
my $count = 0;
my $rc = \$count;
sub inc() {
    $count++;
    return;
}
inc();
inc();
say(${ $rc }, " ", "n=$count");
my $k = 1;
my @same = map { \$k } (1, 2);
say($same[0] == $same[1] ? "same" : "diff", " ", ${ $same[1] });
my @w = (3, 1, 2);
my $lim = 2;
my $rlim = \$lim;
say(join(",", grep { $_ >= $rlim->$* } @w), " ", join(",", sort { $a <=> $b } map { $_ + ${ $rlim } } @w));
my %seen;
my $key = "k";
my $rk = \$key;
$seen{$key} = 1;
$seen{${ $rk } . "2"} = 2;
say(join(",", map { "$_=$seen{$_}" } sort keys %seen));
