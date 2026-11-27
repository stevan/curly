use v5.42;
use experimental 'class';
class A { ADJUST { $self->m } method m { say "A.m" } } class B :isa(A) { field $v = 5; method m { say "B.m v=$v" } } B->new;
