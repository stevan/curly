# t/models/file.py 6428
# kind: dies
# stdin: only
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
my $s1 = <STDIN>; say defined $s1 ? show($s1) : "undef";
my $s2 = <STDIN>; say defined $s2 ? show($s2) : "undef";
die "stdin met its end\n";
