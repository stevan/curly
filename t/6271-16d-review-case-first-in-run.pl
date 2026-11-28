# A \u or \l first in a run ends with it, but for \L\u and \U\l, which perl swaps (T677).
use v5.42;
my $e = "";
say "\U\u$e\Eabc";
say "\L\l$e\EABC";
say "\Q\u$e\Ea.c";
say "\Q\l$e\EA.C";
say "\L\u$e\Eabc";
say "\U\l$e\EABC";
say "\U\uab\Ecd";
say "\L\lAB\ECD";
say "\L\uAB\Ecd";
say "\U\lab\ECD";
say "\L\u$e\Eabc \uxyz";
say "\Q\ua.b\Ec.d";
say "\U\u$e";
say "\u\U$e\Eabc";
