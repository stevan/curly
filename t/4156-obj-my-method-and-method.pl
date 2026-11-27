# kind: refused
# perl warns (R17-03-my-and-public-same): Method b redefined, and the call dies.
use v5.42;
use experimental 'class';
class P { my method b { 1 } method b { 2 } }
