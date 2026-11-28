# check: ok
# kind: same
# PATH is one value on every machine, for perl and for the program (D223):
# a test that prints the machine's own would pass here and fail elsewhere.
use v5.42;
say $ENV{PATH};
