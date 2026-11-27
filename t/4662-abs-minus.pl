# kind: refused
# perl warns: Use of "abs" without parentheses is ambiguous (T485).
use v5.42;
say abs - 5;
