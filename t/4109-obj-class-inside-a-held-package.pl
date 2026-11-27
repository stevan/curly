# kind: refused
# perl runs it: IO::Thing is a package of its own beside IO's.
use v5.42;
use experimental 'class';
class IO::Thing { }
