# kind: refused
# perl prints 0, and the pattern matches: its optimiser looks for 'b&aa' two characters in (T570). The compiler printed 1.
use v5.42;
say "b&aaaa" =~ /b+&(?:a{2}){2}/ ? 1 : 0;
