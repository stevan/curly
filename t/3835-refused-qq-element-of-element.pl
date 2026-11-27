# perl prints 1; in the language since step 13d.
use v5.42;
my %h = (a => { b => 1 });
say qq($h{a}{b});
