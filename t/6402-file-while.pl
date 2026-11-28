# t/models/file.py 6402
# file: zero.txt=a\n0
# file: zeros.txt=0\n0\n\n0\n
# file: blank.txt=\n
# file: empty.txt=
# file: space.txt=\0040\n0.0\n00\n
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $in0, '<', "zero.txt") or die "cannot open zero.txt: $!\n";
while (my $l = <$in0>) { say "while ", show($l) }
say eof($in0) ? "eof" : "more";
close $in0;
open(my $in1, '<', "zeros.txt") or die "cannot open zeros.txt: $!\n";
while (my $l = <$in1>) { say "while ", show($l) }
say eof($in1) ? "eof" : "more";
close $in1;
open(my $in2, '<', "blank.txt") or die "cannot open blank.txt: $!\n";
while (my $l = <$in2>) { say "while ", show($l) }
say eof($in2) ? "eof" : "more";
close $in2;
open(my $in3, '<', "empty.txt") or die "cannot open empty.txt: $!\n";
while (my $l = <$in3>) { say "while ", show($l) }
say eof($in3) ? "eof" : "more";
close $in3;
open(my $in4, '<', "space.txt") or die "cannot open space.txt: $!\n";
while (my $l = <$in4>) { say "while ", show($l) }
say eof($in4) ? "eof" : "more";
close $in4;
