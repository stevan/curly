# kind: refused
# perl does not compile it (R17-13-attr-blank): Invalid separator character '(' in attribute list.
use v5.42;
use experimental 'class';
class P { field $x :param (y); }
