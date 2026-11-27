# t/models/io.py 4760
# kind: fault
# stdin: 
use v5.42;
say "before";
chomp(my $l = <STDIN>);
say "not reached";
