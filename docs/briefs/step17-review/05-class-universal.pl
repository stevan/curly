use v5.42;
use experimental 'class';
class P { method v { "pv" } } class UNIVERSAL { method v { "uv" } } class Q { } say Q->new->v;
