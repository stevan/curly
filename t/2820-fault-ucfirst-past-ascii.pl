# perl gives the capital E with an acute, by its tables (titlecase),
# and so does the language since step 16d (D257).
use v5.42;
use utf8;
use open ":std", ":encoding(UTF-8)";
say ucfirst("aé");
say ucfirst("éa");
