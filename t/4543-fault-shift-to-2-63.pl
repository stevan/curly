# kind: fault
# perl prints 9223372036854775808 (T474).
use v5.42;
say 1 << 62;
say 1 << 63;
