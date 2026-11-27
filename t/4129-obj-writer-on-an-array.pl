# kind: refused
# perl dies (17-writer-array): Cannot apply a :writer attribute to a non-scalar field.
use v5.42;
use experimental 'class';
class P { field @a :writer; }
