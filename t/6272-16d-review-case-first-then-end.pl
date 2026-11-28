# kind: refused
# perl prints ABC: its own answer (T677).
use v5.42;
say "\U\u\Eabc";
