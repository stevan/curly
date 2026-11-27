# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
class H { field %h = (1, 2, 3); }
say(1);
H->new;
say(2);
