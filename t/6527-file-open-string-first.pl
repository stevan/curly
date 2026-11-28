# kind: refused
# perl opens the file as a handle named x, and warns: Name "main::x" used only once.
use v5.42;
open('x', '<', 'in.txt');
