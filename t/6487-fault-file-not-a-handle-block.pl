# t/models/file.py 6487
# kind: fault
use v5.42;
my %h = (out => [1]);
say "before";
print { $h{out} } "text";
