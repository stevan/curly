# By hand, with perl's answers (make oracle): the lists repeated that D247
# lets be: by 1 where nothing passes it by, by a count other than 1, by a
# count that is a variable, a float or a string.
use v5.42;
my $v = 1;
my $n = 1;
my @l = ((7) x 1);
say scalar(@l), " @l";
@l = ($v ? (7) x 2 : 0);
say scalar(@l), " @l";
@l = ($v ? (7) x $n : 0);
say scalar(@l), " @l";
@l = ($v ? (7) x 1.0 : 0);
say scalar(@l), " @l";
@l = ($v ? (7) x "1" : 0);
say scalar(@l), " @l";
@l = ($v ? ((7) x 1)[0] : 0);
say scalar(@l), " @l";
@l = ($v ? 1 : 2, (7) x 1);
say scalar(@l), " @l";
say((7) x 1, "e");
