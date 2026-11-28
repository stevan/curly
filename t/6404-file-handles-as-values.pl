# t/models/file.py 6404
# file: abc.txt=a\nb\nc\nd\ne\nf\ng\n
# file: xy.txt=x\ny\n
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $fh, '<', "abc.txt") or die "cannot open abc.txt: $!\n";
say ref($fh), " ", ref(\$fh), " ", defined($fh) ? "defined" : "undef", " ", $fh ? "true" : "false";
my $copy = $fh;
my $c1 = <$copy>; say show($c1);
say $copy == $fh ? "one" : "two", " ", $copy != $fh ? "differ" : "same";
my %h = (in => $fh);
my @a = ($fh);
my $from = $h{in};
my $c2 = <$from>; say show($c2);
sub next_of($h) { my $l = <$h>; return $l }
say show(next_of($a[0]));
my $reader = sub { my $l = <$fh>; return $l };
say show($reader->());
sub opened($name) { open(my $new, '<', $name) or die "no $name\n"; return $new }
my $other = opened("xy.txt");
say $other == $fh ? "one" : "two", " ", $other != $fh ? "differ" : "same";
my $o1 = <$other>; say show($o1);
try { die $fh } catch ($e) { my $l = <$e>; say "caught ", ref($e), " ", show($l) }
my $r = \$fh; my $through = $r->$*;
my $c3 = <$through>; say show($c3);
open($fh, '<', 'xy.txt') or die "no\n";
my $c4 = <$copy>; say show($c4);
my $c5 = <$from>; say show($c5);
say eof($a[0]) ? "eof" : "more", " ", $copy == $fh ? "one" : "two";
close($copy);
open($copy, '<', 'abc.txt') or die "no\n";
my $c6 = <$fh>; say show($c6);
close($h{in});
close($other);
my @handles = map { opened($_) } "abc.txt", "xy.txt", "abc.txt";
for my $each (@handles) { my $l = <$each>; print $l; close($each) }
my @globs = grep { ref($_) eq "GLOB" } @handles, 5, "GLOB", [1];
say scalar(@globs);
