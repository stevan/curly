# t/models/file.py 6424
# kind: warns
# file: in.txt=a\nb\nc\n
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $fh, '<', "in.txt") or die "cannot open in.txt: $!\n";
while (my $l = <$fh>) { say "while ", show($l) }
open($fh, '<', "in.txt");
my $t2 = <$fh>; say defined $t2 ? show($t2) : "undef";
my $t3 = <$fh>; say defined $t3 ? show($t3) : "undef";
my $t4 = <$fh>; say defined $t4 ? show($t4) : "undef";
say eof($fh) ? "eof" : "more";
my $t5 = <$fh>; say defined $t5 ? show($t5) : "undef";
my @a6 = <$fh>; say scalar(@a6), " lines"; for my $x (@a6) { say show($x) }
die "eof met the end, and no read looked again\n";
