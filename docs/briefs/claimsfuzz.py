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
    # ---- T602: an index that frees the container it indexes
    c('T602', 'TRAPS; D246', 'my $v; sub f() { $v = undef; return "k" } $v->{f()} = 5; say "end";', exit=255, err='Modification of a read-only value attempted'),
    c('T602-read', 'TRAPS; D246', 'my $v = [1, 2]; sub f() { $v = [7, 8]; return 0 } say $v->[f()];', out='\n', err='Use of uninitialized value in say'),
    c('T602-direct', 'TRAPS; D246', 'my $v = [1, 2]; say $v->[($v = [7, 8]) ? 0 : 1];', out='\n', err='Use of uninitialized value in say'),
    c('T602-element', 'TRAPS; D246', 'my @a = ([1]); sub f() { @a = ([5]); return 0 } say $a[0][f()];', out='\n', err='Use of uninitialized value in say'),
    c('T602-held', 'TRAPS; D246', 'my %h; my $r = \\%h; sub f() { $r = {}; return "k" } $r->{f()} = 1; say join(",", keys %h);', out='k\n'),
    c('T602-second-hop', 'TRAPS; D246', 'my $r = [[1]]; sub f() { $r->[0] = [5]; return 0 } say $r->[0][f()];', out='\n', err='Use of uninitialized value in say'),
    c('T602-named', 'TRAPS; D246', 'my @a = (1, 2); sub f() { @a = (5, 6); return 0 } say $a[f()];', out='5\n'),
    # ---- T603: perl 5.42 loses its place after a list repeated by 1
    c('T603', 'TRAPS; D247', 'my $v = 1; my @l = ($v ? (7) x 1 : 0); say scalar(@l), " @l";', out='70 \n'),
    c('T603-and', 'TRAPS; D247', 'my $v = 1; my @l = ($v && (7) x 1); say scalar(@l), " @l";', out='70 \n'),
    c('T603-or', 'TRAPS; D247', 'my $z = 0; my @l = ($z || (7, 8) x 1); say scalar(@l), " @l";', out='780 \n'),
    c('T603-folded', 'TRAPS; D247', 'my $v = 1; my @l = ($v ? (7) x (2 - 1) : 0); say scalar(@l), " @l";', out='70 \n'),
    c('T603-two', 'TRAPS; D247', 'my $v = 1; my @l = ($v ? (7) x 2 : 0); say scalar(@l), " @l";', out='2 7 7\n'),
    c('T603-float', 'TRAPS; D247', 'my $v = 1; my @l = ($v ? (7) x 1.0 : 0); say scalar(@l), " @l";', out='1 7\n'),
    c('T603-string', 'TRAPS; D247', 'my $v = 1; my @l = ($v ? (7) x "1" : 0); say scalar(@l), " @l";', out='1 7\n'),
    c('T603-alone', 'TRAPS; D247', 'my @l = ((7) x 1); say scalar(@l), " @l";', out='1 7\n'),
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
    c('T601-call', 'TRAPS; D245', 'sub g() { return sort { say "c"; $a <=> $b } (2, 1) } sub f() { return (g(), 1) } f(); say "end";', out='end\n'),
    c('T601-call-range', 'TRAPS; D245', 'sub g() { return (1 .. 2) } sub f() { return (g(), 1) } f(); say "end";', out='end\n', err=r'in range \(or flip\)'),
    c('T601-map', 'TRAPS; D245', 'sub f() { return map { say "m"; 1 } (2, 1); } f(); say "end";', out='m\nm\nend\n'),
]
