# t/models/io.py 4714
# stdin: first\nsecond\n\nlast
use v5.42;
chomp(my $a1 = <STDIN>);
say "[$a1]";
my $a2;
chomp($a2 = <STDIN>);
say "[$a2]";
chomp(my $a3 = <STDIN>);
say "[$a3]";
chomp(my $a4 = <STDIN>);
say "[$a4]";
chomp(my $s = "x\n\n");
say length $s;
chomp(my $n = 41);
say $n + 1;
