# t/models/file.py 6426
# kind: dies
# file: cut.txt=x\ny
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $fh, '<', "cut.txt") or die "cannot open cut.txt: $!\n";
my $t1 = <$fh>; say defined $t1 ? show($t1) : "undef";
open(my $other, '<', "cut.txt") or die "cannot open cut.txt: $!\n";
my $t2 = <$fh>; say defined $t2 ? show($t2) : "undef";
die "the last line has no newline: the end was met\n";
