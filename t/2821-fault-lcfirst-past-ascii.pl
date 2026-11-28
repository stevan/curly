# perl gives a small e with an acute, then a; and so does the language
# since step 16d (D257).
use v5.42;
use utf8;
use open ":std", ":encoding(UTF-8)";
say lcfirst("Éa");
