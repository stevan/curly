# t/models/io.py 4766
# kind: fault
# stdin: a\nb\n
use v5.42;
sub lines() { return <STDIN> }
say "before";
my $l = lines();
say "not reached";
