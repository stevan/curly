# kind: refused
# perl dies 'a b' and adds no line, its last item ending in a newline; the language does not look into a join's list (D261), and refuses it.
use v5.42;
my @l = ("a", "b\n");
die join(" ", @l)
    if @l;
