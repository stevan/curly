# kind: refused
# perl gives an element of %!, whether the last error was that one.
use v5.42;
say $!{ENOENT};
