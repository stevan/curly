# check: fails: not by an uncaught die
# kind: dies
# A program that writes to stderr and exits 255 is no uncaught die
# (step 21, D220): Warned.pm marks the exit.
use v5.42;
say "before";
print STDERR "stopped\n";
exit 255;
