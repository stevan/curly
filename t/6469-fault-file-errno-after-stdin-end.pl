# t/models/file.py 6469
# kind: fault
use v5.42;
open(my $no, '<', 'nope.txt');
my $l = <STDIN>;
say defined $l ? "line" : "undef";
say "$!";
