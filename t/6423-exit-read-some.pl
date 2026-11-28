# t/models/file.py 6423
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
my $t1 = <$fh>; say defined $t1 ? show($t1) : "undef";
my $t2 = <$fh>; say defined $t2 ? show($t2) : "undef";
my $t3 = <$fh>; say defined $t3 ? show($t3) : "undef";
die "three lines, and the end not met\n";
