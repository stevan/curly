# Step 13d's statements about perl, as claims.py's rows: references in a
# string. claims.py reads it.
#
#     python3 docs/briefs/claims.py T352 13d-chains
def c(id, where, code, **said):
    return (id, where, code, said)

R = 'my $r = [10, [20, 21], {k => "v"}]; my $h = {a => {b => "hb"}, k => "kv"}; my $v = "sv"; my $s = \\$v; my @a = ([1, 2], [3, 4]); my %g = (a => {b => "B"}, x => [7, 8]); my $i = 1; '

STEP13D = [
    # ---- where perl ends a reference in a string (PLAN 13d; T247, T253)
    c('13d-chains', 'PLAN 13d; TRAPS T247', R + 'say "$r->[0]|$r->[1][1]|$r->[1]->[0]|$r->[2]{k}|$a[1][0]|$a[0]->[1]|$g{a}{b}|$g{x}->[0]|$r->[$i][0]|$h->{a}{b}";',
      out='10|21|20|v|3|2|B|7|20|hb\n'),
    c('13d-whole', 'PLAN 13d; TRAPS T247', R + 'say "@{$r->[1]}|$r->[1]->@*|$r->[1]->$#*|$#{$r}|$s->$*|${$s}|$r->[1]->@[1, 0]|@{ $r->[1] }|${ $s }|$#{ $r }";',
      out='20 21|20 21|1|2|sv|sv|21 20|20 21|sv|2\n'),
    c('13d-text-after', 'PLAN 13d; TRAPS T247', R + 'say "$r->[0] [1]|$r->[0]->foo|$r->[0]::x|$h->{k}::x|$r->[0]-|$r->[0]->|$r->[1]->@*::x|$r->$#*::x|$s->$*::x|${$s}::x|$r->[1]->@[0]::";',
      out='10 [1]|10->foo|10::x|kv::x|10-|10->|20 21::x|2::x|sv::x|sv::x|20::\n'),
    c('13d-element-package', 'PLAN 13d; D92', 'my @a = (1); say "$a[0]::x";', out='1::x\n'),
    c('13d-not-interpolated', 'PLAN 13d', R + 'my $t = "$r->%*|$h->%*|$r->&*|$r->**|$r->[0]->%[0]"; say $t =~ s/0x[0-9a-f]+/A/gr;',
      out='ARRAY(A)->%*|HASH(A)->%*|ARRAY(A)->&*|ARRAY(A)->**|10->%[0]\n'),
    c('13d-after-postfix', 'PLAN 13d; TRAPS T253', R + 'my $t = "$r->[1]->@*[0]|$r->[1]->$#*[0]|$s->$*[0]|$s->$*->[0]|$s->$*{a}|$r->$#*->[0]"; say $t;',
      out='20 21[0]|1[0]|sv[0]|sv->[0]|sv{a}|2->[0]\n'),
    c('13d-after-braces', 'PLAN 13d; TRAPS T253', 'my $a = [7]; my $s = \\$a; say "${$s}->[0]"; my $r = [8, 9]; say "@{$r}[1]";', out='7\n9\n'),
    c('13d-after-braces-dies', 'PLAN 13d; TRAPS T253', 'my $r = [8]; say "@{$r}->[0]";', exit=255, err="Can't use an array as a reference"),
    c('13d-after-last-braces', 'PLAN 13d; TRAPS T253', 'my $r = [8]; say "$#{$r}[0]";', compiles=False, err='syntax error'),
    c('13d-after-slice', 'PLAN 13d', 'my $r = [[5]]; say "$r->@[0]->[0]";', out='5\n'),
    c('13d-after-slice-index', 'PLAN 13d', 'my $r = [[5]]; say "$r->@[0][0]";', compiles=False, err='syntax error'),
    c('13d-hash-slice', 'PLAN 13d; D111', 'my $q = {k => 1, j => 2}; say "$q->@{k}|$q->@{\'k\', \'j\'}";', out='1|1 2\n'),
    c('13d-arrow-then-variable', 'PLAN 13d', 'my $r = [1]; my @x = (2); my $x = 3; say "$r->[0]->@x|$r->[0]->$x";', out='1->2|1->3\n'),
    c('13d-arrow-dollar-hash', 'PLAN 13d', 'my $r = [1]; say "$r->[0]->$#";', exit=255, err=r'\$# is no longer supported'),
    c('13d-index-code', 'PLAN 13d', 'my $r = [1, 2]; my $i = 0; say "$r->[$i+1]|$r->[01]|$r->[ 1 ]"; my $h = {k => 3, "-k" => 4}; say "$h->{ k }|$h->{-k}";', out='2|2|2\n3|4\n'),
    c('13d-braces-code', 'PLAN 13d', 'my $r = [[1]]; my @r = ([2]); say "@{$r ->[0]}|@{$r [0]}|@{ $r->[0] }"; say "${\\ 5}|@{[ 1 + 1 ]}";', out='1|2|1\n5|2\n'),
    c('13d-braces-keys', 'PLAN 13d', 'my %h = (s => [1], q => [2], tr => [3]); my $h = {y => [4], m => [5]}; say "@{$h{s}}|@{$h{q}}|@{$h{tr}}|@{$h->{y}}|@{$h->{m}}";', out='1|2|3|4|5\n'),
    c('13d-dollar-dollar', 'PLAN 13d; D108', 'my $x = 1; my $s = \\$x; my $r = [3]; say "$$s|$$r[0]|@$r|$#$r";', out='1|3|3|0\n'),
    c('13d-qq-brackets', 'PLAN 13d', 'my $r = [1, {k => 2}]; say qq{$r->[1]{k}}; say qq[$r->[0]]; say qq(@{$r}[0]);', out='2\n1\n1\n'),
    # ---- what reads through undef does in a string (PLAN 13d; D107)
    c('13d-undef-whole', 'PLAN 13d; D107', 'my $r; say "a@{$r}b";', exit=255, err='Can\'t use an undefined value as an ARRAY reference'),
    c('13d-undef-postfix-whole', 'PLAN 13d; D107', 'my $r; say "a$r->@*b";', exit=255, err='Can\'t use an undefined value as an ARRAY reference'),
    c('13d-undef-last', 'PLAN 13d; D107', 'my $r; say "a$#{$r}b"; say ref $r; my $s; say "a$s->$#*b"; say ref $s;', out='a-1b\nARRAY\na-1b\nARRAY\n'),
    c('13d-undef-scalar', 'PLAN 13d; D107', 'my $r; say "a${$r}b";', exit=255, err='Can\'t use an undefined value as a SCALAR reference'),
    c('13d-undef-element', 'PLAN 13d; D107', 'my $r = {}; say "a$r->{x}{y}b"; say exists $r->{x} ? "made" : "not";', out='ab\nmade\n', err='uninitialized'),
    c('13d-undef-slice', 'PLAN 13d; D107', 'my $r; say "a$r->@[0, 1]b"; say ref $r;', out='a b\nARRAY\n', err='uninitialized'),
    c('13d-slice-past-the-end', 'PLAN 13d', 'my $r = [5]; say "a$r->@[0, 3]b"; say scalar @$r;', out='a5 b\n1\n', err='uninitialized'),
    c('13d-not-a-reference', 'PLAN 13d', 'my $r = [1]; say "a$r->[0][1]b";', exit=255, err='as an ARRAY ref'),
    c('13d-address', 'PLAN 13d; D112', 'my $r = [[1]]; my $t = "$r->[0]|@{$r}"; say $t =~ s/0x[0-9a-f]+/A/gr;', out='ARRAY(A)|ARRAY(A)\n'),
    # ---- a string is a value made where it stands (PLAN 13d; T196, T235)
    c('13d-made-where-it-stands', 'PLAN 13d; TRAPS T235', 'my $r = [3]; say "$r->[0]-" . ($r->[0] = 5); say "$r->[0]" . ($r->[0] = 6); say "$r->[0]", ($r->[0] = 7); my $x = "x"; say $x . "$r->[0]" . ($r->[0] = 8); say "-$r->@*-" . ($r->[0] = 9);',
      out='3-5\n56\n67\nx78\n-8-9\n'),
    c('13d-made-replaced', 'PLAN 13d; TRAPS T236', 'my $r = [3]; say "$r->[0]", ($r = [5])->[0]; my @l = ("@{$r}", ($r = [7, 8])->[1]); say "@l"; sub f($x) { $x->[0] = 9; return 1; } say "<$r->[0]>", f($r), "<$r->[0]>";', out='35\n5 8\n<7>1<9>\n'),
    c('13d-t230-through', 'PLAN 13d; TRAPS T230, T238', 'my $r = [3]; my @a; $a[$r->[0] = 0] = "a$r->[0]"; say "@a";', out='a0\n'),
    c('13d-t198-through', 'PLAN 13d; TRAPS T198', 'my $r = [3]; my $u; my $t = "t"; $t .= ($u = "a$r->[0]"); say $t, defined $u ? $u : "U"; $t .= ($r->[0] = "a$r->[0]"); say $t, $r->[0];',
      out='ta3U\nta3a3a3\n'),
    c('13d-loop-over-strings', 'PLAN 13d', 'my $m = [8, [4, 9]]; my @seen; for my $t ("$m->[0]", "@{$m->[1]}", "$#{$m}") { push $m->[1]->@*, 0; $m->[0] = 0; push @seen, $t } say join("|", @seen), " ", $m->[1]->$#*;',
      out='8|4 9|1 4\n'),
    # ---- found building step 13d (TRAPS T352)
    c('T352', 'TRAPS; PLAN 13d', 'my $q = {k => 1}; say qq<$q->{k}>;', compiles=False, err='syntax error'),
    c('T353', 'TRAPS; PLAN 13d', 'my $r; say "a$#{$r}b"; say ref $r; my $s; say "a$s->$#*b"; say ref $s;', out='a-1b\nARRAY\na-1b\nARRAY\n'),
    c('T354', 'TRAPS; PLAN 13d', 'my $r = [[5], [6, 7]]; my @x = (2); my $x = 3; my $v = "sv"; my $s = \\$v; say "$r->[0]->@x|$r->[0][0]->$x|$r->@[0]->[0]|$r->[1]->@*[0]|$s->$*->[0]" =~ s/0x[0-9a-f]+/A/gr;', out='ARRAY(A)->2|5->3|5|6 7[0]|sv->[0]\n'),
    c('T352-angle', 'TRAPS; PLAN 13d', 'my $q = "Q"; say qq<a$q->;', out='aQ-\n'),
]
