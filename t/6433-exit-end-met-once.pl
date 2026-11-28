# t/models/file.py 6433
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
my @a1 = <$fh>; say scalar(@a1), " lines"; for my $x (@a1) { say show($x) }
open(my $other, '<', "in.txt") or die "cannot open in.txt: $!\n";
my $t2 = <$fh>; say defined $t2 ? show($t2) : "undef";
my @a3 = <$fh>; say scalar(@a3), " lines"; for my $x (@a3) { say show($x) }
die "the end was met before the second open, and not again\n";
