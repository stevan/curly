# Step 14's statements about perl, as claims.py's rows: closures, calls
# through a reference. claims.py reads it.
#
#     python3 docs/briefs/claims.py T360 T370
def c(id, where, code, **said):
    return (id, where, code, said)

STEP14 = [
    # ---- found proposing step 14 (PLAN 14; TRAPS T360 to T369)
    c('T360', 'TRAPS; PLAN 14', 'my @s; for my $i (1..3) { push @s, sub { return $i } } say join ",", map { $_->() } @s;', out='1,2,3\n'),
    c('T360-c-style', 'TRAPS; PLAN 14', 'my @s; for (my $i = 0; $i < 3; $i++) { push @s, sub { $i } } say join ",", map { $_->() } @s;', out='3,3,3\n'),
    c('T360-my-in-block', 'TRAPS; PLAN 14', 'my @s; for my $i (1..3) { my $j = $i; push @s, sub { $j++ } } say $s[0]->(), $s[0]->(), $s[1]->();', out='122\n'),
    c('T360-counter', 'TRAPS; PLAN 14', 'sub counter() { my $n = 0; return sub { return ++$n } } my $c = counter(); my $d = counter(); say $c->(), $c->(), $d->();', out='121\n'),
    c('T360-shared', 'TRAPS; PLAN 14', 'my $x = 1; my $f = sub { $x }; $x = 2; say $f->(); my $g = sub { $x = 5 }; $g->(); say $x;', out='2\n5\n'),
    c('T11-closure', 'TRAPS T11; PLAN 14', 'my @a=(1,2); my @s; for my $x (@a) { push @s, sub { $x } } $a[0]=9; say $s[0]->();', out='9\n'),
    c('T361-values', 'TRAPS; PLAN 14', 'my %h = (a => 1); my @s; for my $v (values %h) { push @s, sub { $v } } $h{a} = 9; say $s[0]->();', out='9\n'),
    c('T361-keys', 'TRAPS; PLAN 14', 'my %h = (a => 1); my @s; for my $k (keys %h) { push @s, sub { $k } } delete $h{a}; say $s[0]->();', out='a\n'),
    c('T361-scalars', 'TRAPS; PLAN 14', 'my ($p, $q) = (1, 2); my @s; for my $x ($p, $q) { push @s, sub { $x } } $p = 9; say $s[0]->();', out='9\n'),
    c('T361-shift', 'TRAPS; PLAN 14', 'my @a = (1,2,3); my @s; for my $x (@a) { push @s, sub { $x } } push @a, 4; shift @a; say $s[0]->(), $s[2]->();', out='13\n'),
    c('T362', 'TRAPS; PLAN 14', 'my @a = (1,2); my @s = map { sub { $_ } } @a; say defined $s[0]->() ? "def" : "undef";', out='undef\n'),
    c('T363-constant', 'TRAPS; PLAN 14; D161', 'my @s; for my $i (1..2) { push @s, sub { 1 } } say $s[0] == $s[1] ? "same" : "diff";', out='same\n'),
    c('T363-closure', 'TRAPS; PLAN 14; D161', 'my @s; for my $i (1..2) { push @s, sub { $i } } say $s[0] == $s[1] ? "same" : "diff";', out='diff\n'),
    c('T363-file-variable', 'TRAPS; PLAN 14; D161', 'my $g = 1; sub mk() { return sub { $g } } say mk() == mk() ? "same" : "diff";', out='diff\n'),
    c('T363-sub-constant', 'TRAPS; PLAN 14; D161', 'sub mk() { return sub { 1 } } say mk() == mk() ? "same" : "diff";', out='same\n'),
    c('T364-context', 'TRAPS; PLAN 14', 'my $f = sub { return (1,2,3) }; my @l = $f->(); my $c = $f->(); say scalar(@l), $c;', out='33\n'),
    c('T364-late', 'TRAPS; PLAN 14; D14', 'my $total = 5; my $step = sub { $total += 100; return 1 }; say $total + $step->();', out='106\n'),
    c('T364-list', 'TRAPS; PLAN 14; D76', 'my @l; my $x = 1; my $bump = sub { $x = 9; 0 }; @l = ($x, $bump->()); say "@l";', out='9 0\n'),
    c('T365', 'TRAPS; PLAN 14; D165', 'my $f = sub { last }; for my $i (1..3) { say $i; $f->() } say "done";', out='1\ndone\n', err='Exiting subroutine via last'),
    c('T366-count', 'TRAPS; PLAN 14; D164', 'my $f = sub () { 42 }; say $f->(1);', exit=255, err='Too many arguments for subroutine'),
    c('T366-undef', 'TRAPS; PLAN 14; D164', 'my $f; $f->();', exit=255, err="Can't use an undefined value as a subroutine reference"),
    c('T366-array', 'TRAPS; PLAN 14; D164', 'my $f = [1]; $f->();', exit=255, err='Not a CODE reference'),
    c('T366-number', 'TRAPS; PLAN 14; D164', 'my $f = 5; $f->();', exit=255, err='as a subroutine ref while "strict refs"'),
    c('T367', 'TRAPS; PLAN 14', 'my %d = (add => sub ($x, $y) { $x + $y }); my @fs = (sub { 7 }); say $d{add}->(1,2), $fs[0](), $d{add}(3,4); my $add = sub ($x) { sub ($y) { $x + $y } }; say $add->(1)->(2), $add->(1)(2); say sub { 3 }->();',
      out='377\n33\n3\n'),
    c('T368', 'TRAPS; PLAN 14', 'sub named($x) { return $x + 1 } my $r = \\&named; say $r->(1), ref($r), $r == \\&named ? "same" : "diff"; my $f = sub ($n) { return $n <= 1 ? 1 : $n * __SUB__->($n - 1) }; say $f->(5);',
      out='2CODEsame\n120\n'),
    c('T369-my-sub', 'TRAPS; PLAN 14; D160', 'my sub fact($n) { return $n <= 1 ? 1 : $n * fact($n - 1) } say fact(5);', exit=255, err='Undefined subroutine &main::fact'),
    c('T369-state', 'TRAPS; PLAN 14; D160', 'my @s; for my $i (1..2) { push @s, sub { state $n = 0; return ++$n } } say $s[0]->(), $s[0]->(), $s[1]->();', out='121\n'),
    # ---- found by the review of step 14 (PLAN 14, "What the review found"; TRAPS T370 to T376)
    c('T370-call', 'TRAPS; PLAN 14; D166', 'sub arg() { say "arg"; 1 } my $f = sub ($x) { say "called"; $x }; sub fn() { say "fn"; $f } fn()->(arg());', out='arg\nfn\ncalled\n'),
    c('T370-index', 'TRAPS; PLAN 14; D166', 'my $i = 0; my @fs = (sub { "zero" }, sub { "one" }); say $fs[$i]->($i = 1);', out='one\n'),
    c('T370-places', 'TRAPS; PLAN 14; D166', 'my $x = 1; sub mk() { $x = 5; return sub ($v) { $v } } say mk()->($x + 0), mk()->($x);', out='15\n'),
    c('T371-ternary', 'TRAPS; PLAN 14; D166', 'my ($p, $q, $c) = (1, 2, 1); my @s; for my $x ($c ? $p : $q) { push @s, sub { $x } } $p = 9; say $s[0]->();', out='9\n'),
    c('T371-grep', 'TRAPS; PLAN 14; D166', 'my @a = (1, 2); my @s; for my $x (@a) { for my $y (grep { 1 } $x) { push @s, sub { $y } } } $a[0] = 9; say $s[0]->();', out='9\n'),
    c('T372', 'TRAPS; PLAN 14; D166', 'my @a = (1, 2); my @s; for my $x (@a) { push @s, sub { $x = 5 } } $s[0]->(); say "@a";', out='5 2\n'),
    c('T373', 'TRAPS; PLAN 14; D166', 'sub nm() { return sub { 42 } } my $r = \\&nm->(); say ref($r);', out='SCALAR\n'),
    c('T374', 'TRAPS; PLAN 14; D166', 'sub mk2() { return sub { 12 } } say mk2()();', compiles=False, err='syntax error'),
    c('T375', 'TRAPS; PLAN 14; D166', 'my $g = 1; my @s; for my $i (1..2) { push @s, sub { sub { $g } } } say $s[0] == $s[1] ? "same" : "diff";', out='diff\n'),
    c('T376', 'TRAPS; PLAN 14; D166', 'my $f = sub { $f->() };', compiles=False, err='Global symbol "\\$f"'),
    c('T366-default-closure', 'PLAN 14; D166', 'sub g($x, $f = sub { $x }) { $x = 9; return $f->() } say g(1);', out='9\n'),
]
