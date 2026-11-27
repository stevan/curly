# t/models/io.py 4716
# stdin: 0\n0
use v5.42;
my $l = <STDIN>;
say $l ? "true" : "false";
if (my $m = <STDIN>) { say "true" } else { say "false: [$m]" }
my $n = <STDIN> // "end";
say $n;
my $o = <STDIN> || "nothing";
say $o;
