# perl runs it: '1\n'; in the language since step 13d.
use v5.42;
my %g = (a => {b => 1});
say "$g{a}{b}";
