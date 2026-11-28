# kind: refused
# perl does not compile it under use v5.42: Bareword "STDOUT" not allowed while "strict subs" in use.
use v5.42;
printf {STDOUT} "%s\n", "x";
