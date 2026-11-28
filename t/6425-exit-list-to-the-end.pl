# t/models/file.py 6425
# kind: dies
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
open(my $other, '<', "in.txt") or die "cannot open in.txt: $!\n";
my @a1 = <$fh>; say scalar(@a1), " lines"; for my $x (@a1) { say show($x) }
die "a list met the end\n";
