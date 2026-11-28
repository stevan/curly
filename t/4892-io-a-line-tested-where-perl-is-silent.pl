# stdin: a\n0
# Where perl tests a line assigned for truth and says nothing (T518): an
# if with an else, an elsif's test, a ? :, under a !, and on the right of
# && and ||. The last line, 0, is false in each, and so is the end.
use v5.42;
my $l;
if ($l = <STDIN>) { print "if [$l]" } else { say "if false" }
if ($l = <STDIN>) { say "if [$l]" } else { say "if false [$l]" }
if (@ARGV) { say "args" } elsif ($l = <STDIN>) { say "elsif [$l]" } else { say "elsif false" }
if (@ARGV) { say "args" } elsif ($l = <STDIN>) { say "elsif [$l]" }
my $t = ($l = <STDIN>) ? "true" : "false";
say $t;
$l = "x";
say "end" if !($l = <STDIN>);
say defined $l ? "defined" : "undef";
my $go = 1;
my $n = 0;
while ($go && ($l = <STDIN>)) { $n++ }
say $n;
my $m = @ARGV || ($l = <STDIN>);
say defined $m ? "defined" : "undef";
