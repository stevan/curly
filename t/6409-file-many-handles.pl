# t/models/file.py 6409
# env: CURLY_GC_STRESS=0 CURLY_GC_POISON=0
# file: in.txt=a\nb\n
use v5.42;
my $read = "";
for my $i (1 .. 1500) {
    open(my $fh, '<', 'in.txt') or die "open $i: $!\n";
    my $l = <$fh>;
    $read = $l if $i == 1500;
}
print $read;
for my $i (1 .. 1500) {
    open(my $out, '>>', 'out.txt') or die "open $i: $!\n";
    print $out "x";
    close($out);
}
open(my $in, '<', 'out.txt') or die "no\n";
my $made = <$in>;
say length($made);
