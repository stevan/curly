# kind: refused
# perl prints 0, and the pattern matches (T570). The compiler printed 1.
use v5.42;
say "bbaaaaaab" =~ /b+(?:(?:a){2}){3,}./ ? 1 : 0;
