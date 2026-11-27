# kind: dies
# stdin: a\nb\n
# Once a line has been read, perl's message for a die names the handle
# and how many lines it has given (T516); not before.
use v5.42;
my $e;
try { die "before" } catch ($x) { $e = $x }
print $e;
my $l = <STDIN>;
try { die "one" } catch ($x) { $e = $x }
print $e;
my @rest = <STDIN>;
my $none = <STDIN>;
try { die "after" } catch ($x) { $e = $x }
print $e;
try { die "with a newline\n" } catch ($x) { $e = $x }
print $e;
die "uncaught";
