# t/models/file.py 6410
# kind: warns
# stdin: s1\ns2\ns3
# file: in.txt=f1\nf2\n
# file: empty.txt=
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
warn "before";
my $s1 = <STDIN>; say defined $s1 ? show($s1) : "undef";
warn "stdin read";
open(my $fh, '<', "empty.txt");
warn "opened";
my $t2 = <$fh>; say defined $t2 ? show($t2) : "undef";
warn "nothing read from the file";
my $s3 = <STDIN>; say defined $s3 ? show($s3) : "undef";
warn "stdin again";
open(my $in, '<', "in.txt");
my $t4 = <$in>; say defined $t4 ? show($t4) : "undef";
close($in);
warn "read and closed";
say eof(STDIN) ? "eof" : "more";
warn "eof of stdin";
open($in, '<', "in.txt");
say eof($in) ? "eof" : "more";
warn "eof of the file";
my $s5 = <STDIN>; say defined $s5 ? show($s5) : "undef";
my $s6 = <STDIN>; say defined $s6 ? show($s6) : "undef";
warn "stdin at its end";
try { die "caught" } catch ($e) { print "c: $e" }
