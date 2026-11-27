# kind: fault
# perl shifts by 0 or 1 by the string's past (T475).
use v5.42;
say 1 << "0.99999999999999995";
