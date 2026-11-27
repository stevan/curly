# kind: refused
# perl asks of STDIN.
use v5.42;
say eof STDIN ? 1 : 0;
