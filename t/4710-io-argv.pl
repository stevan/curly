# t/models/io.py 4710
# args: one 2 three-3 0 -x 1.5
use v5.42;
say scalar(@ARGV);
say "@ARGV";
say $#ARGV;
say $ARGV[0], "|", $ARGV[-1];
say $ARGV[1] + $ARGV[5];
my $first = shift @ARGV;
say $first, " ", scalar(@ARGV);
push @ARGV, "last";
say join(",", @ARGV);
for my $a1 (@ARGV) { print length($a1); }
say "";
sub show(@all) { return join("+", @all) }
say show(@ARGV);
my @sorted = sort @ARGV;
say "@sorted";
say defined $ARGV[20] ? "defined" : "undef";
@ARGV = ();
say scalar(@ARGV);
