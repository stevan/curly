# kind: fault
# perl gives ("\xe9"), folding by its tables (D230).
use v5.42;
use open ":std", ":encoding(UTF-8)";
my @l = ("ab" =~ /(B)/i);
say "@l";
@l = ("a\xe9" =~ /(A)/i);
say "@l";
