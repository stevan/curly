# t/models/file.py 6406
# file: bytes.txt=caf\0303\0251\n\0377\0200\n\0000 nul\n
# file: crlf.txt=a\0015\nb\0015\n\0015c
# file: tabs.txt=\0011\n \n
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $fh, '<', "bytes.txt") or die "cannot open bytes.txt: $!\n";
my $t1 = <$fh>; say defined $t1 ? show($t1) : "undef";
my @a2 = <$fh>; say scalar(@a2), " lines"; for my $x (@a2) { say show($x) }
close($fh);
open($fh, '<', "crlf.txt") or die "cannot open crlf.txt: $!\n";
my $t3 = <$fh>; say defined $t3 ? show($t3) : "undef";
my @a4 = <$fh>; say scalar(@a4), " lines"; for my $x (@a4) { say show($x) }
close($fh);
open($fh, '<', "tabs.txt") or die "cannot open tabs.txt: $!\n";
my $t5 = <$fh>; say defined $t5 ? show($t5) : "undef";
my @a6 = <$fh>; say scalar(@a6), " lines"; for my $x (@a6) { say show($x) }
close($fh);
