"""D260: every left side that could stand before `or`/`and`, by every
statement after the word, in every place a statement stands."""
import itertools

LEFTS = [
    '$z', '$one', '!$z', 'not $z', '$z == 0', '$z + $one', '$z ? 0 : 1', '$z && $one', '$z || $z', '$u // 0',
    'f0()', 'f1()', 'fl()', 'fe()', '@e', '@a', '%h', 'scalar(@e)', 'scalar @a', '$a[0]', '$a[9]', '$h{no}', '$r->[0]',
    'defined $u', 'exists $h{k}', 'delete $h{k}', 'length $s', 'pop @a', 'shift(@e)', 'push @a, 0', 'push(@e, 0)',
    'my $n = $z', 'my $n = f1()', 'my $n = @e', 'my $n = @a', 'my ($n) = @a', 'my @n = @e', 'my $n = fl()', 'my ($n) = fl()',
    '$v = $z', '$v = 0', '$v = 1', '$v = f0()', '$v += 0', '$v .= ""', '$v //= 0', '$v ||= 0', '$v++', '++$v', '$v--',
    '($v) = @e', '@a = ()', '%h = ()', '$a[0] = 0', '$h{k} = 0', '$r->[0] = 0', '($v = 0)', '(($z))', '($z, $one)', '"0.0"', '"00"', '"0"', '""',
    'say "p"', 'print ""', 'chomp $s', 'undef $v', '$#a = -1', 'substr($s, 0, 1, "")', 'sort @a', 'reverse @a', 'join("", @e)', 'scalar reverse("0")',
    'map { $_ } @e', 'grep { $_ } @a', '$z or $one', '$one and $z', '$z xor $one', 'return 0', 'die "l\\n"', 'warn "w\\n"',
    '$one .. $z', 'keys %h', 'values %h', 'sprintf("%d", 0)', '$cr->()', '\\@e', '[]', '{}', '+{}', 'sub { 0 }', '__LINE__', 'true', 'false', 'undef', '0', '1',
    'lc "0"', 'ref $z', '-$z', '$z x 3', '$z . ""', '$z <=> $one', '$s eq "s"', '"@e"', '"$z"', 'qw()', 'qw(a)',
]
RIGHTS = ['die "d\\n"', 'die', 'return', 'return 7', 'return (7, 8)', 'last', 'next', 'last L', 'next L', 'die "a", "b\\n"', 'warn "w\\n"', 'say "r"', 'exit']

PRE = '''my $z = 0; my $one = 1; my $u; my $v = 5; my $s = "s"; my @e = (); my @a = (4, 0); my %h = (k => 0); my $r = [0]; my $cr = sub { return 0; };
sub f0() { return 0; } sub f1() { return 1; } sub fl() { return (3, 0); } sub fe() { return; }
'''


def wrap(kind, stmt):
    if kind == 'top':
        return 'L: for my $i (1 .. 2) { say "i$i"; %s; say "past"; }\nsay "v", $v // "u", " a@a";\n' % stmt
    if kind == 'sub':
        return 'sub g() { L: for my $i (1 .. 2) { say "i$i"; %s; say "past"; } return "end"; }\nsay "[", join(",", g()), "]";\nsay "v", $v // "u", " a@a";\n' % stmt
    if kind == 'last':
        return 'sub g() { %s }\nmy @got = (g());\nsay scalar(@got), ":", join(",", map { $_ // "u" } @got);\n' % stmt
    if kind == 'lasts':
        return 'sub g() { %s }\nmy $got = g();\nsay $got // "u";\n' % stmt
    raise ValueError(kind)


def cases():
    n = 0
    for left in LEFTS:
        for word in ('or', 'and'):
            for right in RIGHTS:
                n += 1
                # every left with die and return; the rest sampled by turns
                if right not in ('die "d\\n"', 'return 7') and n % 5:
                    continue
                kinds = ['top', 'sub'] if not right.startswith('return') else ['sub']
                if right in ('die "d\\n"', 'return 7', 'return (7, 8)', 'return', 'die'):
                    kinds.append('last' if n % 2 else 'lasts')
                for kind in kinds:
                    if kind in ('last', 'lasts') and ('L' in right.split()[-1:] or right in ('last', 'next')):
                        continue
                    yield ('%04d%s' % (n, kind), PRE + wrap(kind, '%s %s %s' % (left, word, right)))
