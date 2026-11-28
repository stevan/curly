# kind: refused
# perl prints 0, and the pattern matches (T570).
use v5.42;
say "b&xababxabab" =~ /b+&(?:x(?:ab){2}){2}/ ? 1 : 0;
