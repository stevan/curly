# kind: refused
# perl says true, and warns: Filehandle STDOUT opened only for output.
use v5.42;
say eof(STDOUT) ? 1 : 0;
