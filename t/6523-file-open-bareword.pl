# kind: refused
# perl does not compile it: Bareword filehandle "FH" not allowed under 'no feature "bareword_filehandles"'.
use v5.42;
open(FH, '<', 'in.txt');
