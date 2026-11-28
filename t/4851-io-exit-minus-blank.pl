# kind: refused
# perl exits 255, and warns: Use of "exit" without parentheses is ambiguous (T517).
use v5.42;
exit - 1;
