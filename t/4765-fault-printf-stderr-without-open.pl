# t/models/io.py 4765
# kind: fault
use v5.42;
use utf8;
say "before";
printf STDERR "%s\n", "é";
say "not reached";
