# kind: refused
# perl opens the file as its stdin.
use v5.42;
open(STDIN, '<', 'in.txt');
