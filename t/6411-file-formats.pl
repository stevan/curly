# t/models/file.py 6411
use v5.42;
open(my $out, '>', "f.txt") or die "cannot open f.txt: $!\n";
sub report($to, $name, $n) { printf {$to} "%-6s|%4d|%5.1f|%x\n", $name, $n, $n / 3, $n; return; }
report($out, "ab", 7);
report($out, "longer", 1234);
report($out, "", 0);
report($out, "q", 255);
my %to = (log => $out);
say { $to{log} } "through a hash ", 1 + 1;
my @outs = ($out);
print { $outs[0] } "through an array\n";
my $pick = 1;
print { $pick ? $out : $outs[0] } "picked\n";
printf $out "%s\n", "plain" if $pick;
say $out "no" unless $pick;
print $out "each $_\n" for 1 .. 3;
print $pick if $pick;
print $pick x 2, "\n";
say $pick != 2 ? "ne" : "eq";
say $pick eq "1" ? "eq" : "ne";
sub last_value($to) { print $to "in a sub\n" }
say last_value($out) ? "true" : "false";
close($out);
open(my $in, '<', "f.txt") or die "cannot open f.txt: $!\n";
print <$in>;
say eof($in) ? "eof" : "more";
