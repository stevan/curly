# kind: refused
# perl asks of the files named in @ARGV, or stdin (T509).
use v5.42;
say eof() ? 1 : 0;
