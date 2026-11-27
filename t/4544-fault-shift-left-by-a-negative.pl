# kind: fault
# perl shifts the other way: 9223372036854775808.
use v5.42;
say 1 >> -63;
