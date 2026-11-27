# t/models/io.py 4713
# kind: warns
use v5.42;
say "before";
printf STDERR "%d-%s\n", 5, "a";
printf STDERR "%5.1f|%-3s|\n", 2.25, "b";
printf STDERR "%x\n", 255;
say "after";
