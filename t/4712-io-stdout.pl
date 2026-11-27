# t/models/io.py 4712
use v5.42;
say STDOUT "a", 1;
print STDOUT "b", "\n";
printf STDOUT "%03d|%s|%.2f\n", 7, "x", 1.5;
printf STDOUT "%s\n", "no brackets";
my @l = ("p", "q");
say STDOUT @l;
printf "%d\n", 9;
say STDOUT "on" if 1;
