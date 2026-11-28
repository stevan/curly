# t/models/file.py 6422
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
while (my $l = <$fh>) { say "while ", show($l) }
die "the end was met\n";
