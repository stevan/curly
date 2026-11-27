# kind: refused
# perl dies (R17-05-class-carp): Cannot create class Carp as it already has a non-empty @ISA.
use v5.42;
use experimental 'class';
class Carp { }
