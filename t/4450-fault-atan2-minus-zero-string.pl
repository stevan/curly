# kind: fault
# perl prints pi, or 0 once the string has been added to (T484).
use v5.42;
say atan2(0, "0");
say atan2(0, "-0");
