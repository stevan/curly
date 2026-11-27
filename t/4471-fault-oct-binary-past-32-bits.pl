# kind: fault
# perl warns: Binary number > 0b11111111111111111111111111111111 non-portable.
use v5.42;
say oct("0b" . "1" x 33);
