# kind: same
# A match a sub gives back, from the independent review of step 19: with one
# group or none it is one value or a list by where the call stands (D235);
# a failed one is nothing among arguments, so the argument after it moves up.
use v5.42;
sub digits($s) { return $s =~ /(\d+)/; }
sub has_z($s) { return $s =~ /z/; }
sub last_one($s) { $s =~ /(\d+)/ }
sub pair($x, $y = "d") { say "$x $y"; }
sub bang($x) { $x . "!" }
sub every($t) { return $t =~ /./g; }
sub one($t) { $t =~ /(b)/ }
sub two($t) { return $t =~ /(.)(.)/; }
my @l = digits("a12");
say "@l";
my $x = digits("a12");
say $x;
my ($y) = digits("a12");
say $y;
@l = has_z("a");
say scalar(@l);
$x = has_z("a");
say "[$x]";
@l = last_one("a12");
say "@l";
$x = last_one("a12");
say $x;
pair("a" =~ /z/, "x");
pair("a" =~ /a/, "x");
say bang("a") =~ /a!/;
say bang("a") =~ /(.)!/;
@l = every("abc");
say "@l";
say scalar(@l);
say one("abc");
say one("x") ? "y" : "n";
@l = one("x");
say scalar(@l);
my ($p, $q) = two("abc");
say "$p$q";
my $f = sub ($t) { $t =~ /(a)(b)/ };
@l = $f->("ab");
say "@l";
my @w = ("a1", "b2");
my @subs = map { my $w = $_; sub { $w =~ /(\d)/ } } @w;
for my $g (@subs) { say $g->(); }
