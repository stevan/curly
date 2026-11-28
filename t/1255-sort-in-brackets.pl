# perl takes it; with more after the bracket it warns (T190, D87). D262
# takes it in, the bracket hard against the word.
use v5.42;
my @a = (3, 1, 2);
my @r = sort(@a);
say "@r";
