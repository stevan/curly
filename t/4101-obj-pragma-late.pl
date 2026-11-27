# kind: refused
# perl runs it (R17-17-pragma-late): the pragma may stand after a statement.
use v5.42;
use experimental 'class';
say "a";
use experimental 'class';
