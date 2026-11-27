# The fuzzer's statements about perl (docs/briefs/fuzz/), as claims.py's
# rows: the WRONGs it found, T600 on. claims.py reads it.
#
#     python3 docs/briefs/claims.py T600 T601
def c(id, where, code, **said):
    return (id, where, code, said)

FUZZ = [
    # ---- T600: a range given back to a call for nothing is a flip-flop
    c('T600', 'TRAPS; D245', 'sub a() { say "a"; 0 } sub b() { say "b"; 3 } sub f() { return (a() .. b()); } f(); say "end";', out='a\nend\n'),
    c('T600-list', 'TRAPS; D245', 'sub a() { say "a"; 0 } sub b() { say "b"; 3 } sub f() { return (a() .. b()); } my @l = f(); say scalar(@l);', out='a\nb\n4\n'),
    c('T600-constant', 'TRAPS; D245', 'my $n = 2; sub f() { return (0 .. $n); } f(); say "end";', out='end\n', err=r'Use of uninitialized value \$\. in range \(or flip\)'),
    c('T600-last', 'TRAPS; D245', 'my $n = 2; sub f() { (1 .. $n) } f(); say "end";', out='end\n', err=r'in range \(or flip\)'),
    c('T600-anon', 'TRAPS; D245', 'my $n = 2; my $f = sub { return (1 .. $n) }; $f->(); say "end";', out='end\n', err=r'in range \(or flip\)'),
    c('T600-repeat', 'TRAPS; D245', 'sub f() { return (sort { $a <=> $b } (2, 1)) x 2; } f(); say "end";', out='end\n', err=r'Use of uninitialized value in repeat \(x\)'),
    c('T600-reverse', 'TRAPS; D245', 'my @a = (1, undef); sub f() { return reverse(@a); } f(); say "end";', out='end\n', err='Use of uninitialized value'),
    c('T600-reverse-list', 'TRAPS; D245', 'my @a = (1, 2); sub f() { return reverse(@a); } my @b = f(); say "@b";', out='2 1\n'),
    # ---- T601: a sort given back to a call for nothing is skipped
    c('T601', 'TRAPS; D245', 'sub f() { return sort { say "cmp"; $a <=> $b } (2, 1); } f(); say "end";', out='end\n'),
    c('T601-list-worked-out', 'TRAPS; D245', 'sub p($x) { say "p$x"; $x } sub f() { return sort { say "cmp"; $a <=> $b } (p(2), p(1)); } f(); say "end";', out='p2\np1\nend\n'),
    c('T601-last', 'TRAPS; D245', 'sub f() { sort { say "cmp"; $a <=> $b } (2, 1) } f(); say "end";', out='end\n'),
    c('T601-branch', 'TRAPS; D245', 'sub f() { return 1 ? (sort { say "cmp"; $a <=> $b } (2, 1)) : 0; } f(); say "end";', out='end\n'),
    c('T601-right', 'TRAPS; D245', 'sub f($c) { return $c || sort { say "cmp"; $a <=> $b } (2, 1); } f(0); say "end";', out='end\n'),
    c('T601-item', 'TRAPS; D245', 'sub f() { return (1, sort { say "cmp"; $a <=> $b } (2, 1)); } f(); say "end";', out='end\n'),
    c('T601-plus', 'TRAPS; D245', 'sub f() { return +(sort { say "cmp"; $a <=> $b } (2, 1)); } f(); say "end";', out='end\n'),
    c('T601-for', 'TRAPS; D245', 'sub f() { return sort { say "cmp"; $a <=> $b } (2, 1); } f() for 1 .. 2; say "end";', out='end\n'),
    c('T601-list', 'TRAPS; D245', 'sub f() { return sort { say "cmp"; $a <=> $b } (2, 1); } my @x = f(); say "@x";', out='cmp\n1 2\n'),
    c('T601-inside', 'TRAPS; D245', 'sub f() { return join(",", sort { say "cmp"; $a <=> $b } (2, 1)); } f(); say "end";', out='cmp\nend\n'),
    c('T601-map', 'TRAPS; D245', 'sub f() { return map { say "m"; 1 } (2, 1); } f(); say "end";', out='m\nm\nend\n'),
]
