"""D250, D258, D262 and D251/D252 as operands: what may follow `scalar X`,
`scalar reverse`, `sort(...)`, and where the new statements may stand."""

ARRS = ['@a', '%h', 'keys %h', 'values %h', '$r->@*', '@{$r}', '@{ $r }', '$hr->%*', '%{$hr}', 'keys $hr->%*', 'keys %{$hr}', '$a[3]->@*', '@{$a[3]}', '@$r', 'reverse "ab", "c"', 'reverse(@a)', 'reverse @a']
AFTER = ['', '+ 1', '- 1', '-1', '* 2', '/ 2', '% 2', '** 2', '. "x"', 'x 2', '== 4', '!= 4', '< 9', '<=> 2', 'eq "4"', 'lt "9"', '&& "y"', '|| "n"', '// "d"', '? "t" : "f"',
         '.. 5', ', "z"', '=> "z"', 'and say "w"', 'or say "w"', 'if 1', 'for 1', '[0]', '{a}', '->[0]', '++', '= 5', '=~ 4', '& 1', '| 1', '<< 1', '>= 1', 'ne 1', 'cmp 1', 'xor 1', ')', '()', '(0)', '->@*', 'x= 2', '+= 1', '!', '~~ 1', 'isa X', '^^ 1', ': 1', '\n+ 1', '# c\n. "x"']
PRE = 'my @a = (5, 6, 7, [1, 2]); my %h = (a => 1, b => 2, c => 3, d => 4); my $r = [1, 2, 3, 4]; my $hr = { a => 1, b => 2, c => 3, d => 4 };\n'

SORTS = ['sort(@a)', 'sort({ $a <=> $b } @a)', 'sort(keys %h)', 'sort(@a, 1)', 'sort((@a))', 'sort(reverse @a)', 'sort()', 'sort(sort @a)', 'sort(f(@a))', 'sort(f @a)', 'sort(f (@a))', 'sort(f, @a)',
         'sort(lc "B", "a")', 'sort(lc("B"), "a")', 'sort(-1, -2)', 'sort((3), 2)', 'sort((3, 2)[0, 1])', 'sort(@a[0, 1])', 'sort($r->@*)', 'sort(@{$r})', 'sort($a[0], 1)', 'sort($x, 1)', 'sort($x)', 'sort($x + 1, 0)',
         'sort($r->[0], 0)', 'sort("b", "a")', 'sort(qw(b a))', 'sort(1 .. 3)', 'sort({ $b <=> $a } 1 .. 3)', 'sort({ $b <=> $a } @a, 0)', 'sort({ $b <=> $a } (@a, 0))', 'sort({ $b <=> $a } f(@a))',
         'sort({ lc($a) cmp lc($b) } qw(b A))', 'sort({ $a <=> $b })', 'sort({ $a <=> $b } )', 'sort({ $a <=> $b }, @a)', 'sort(({ $a <=> $b } @a))', 'sort(+@a)', 'sort(+(@a))', 'sort(+f(@a))',
         'sort(scalar(@a), 2)', 'sort(scalar @a, 2)', 'sort(map { $_ } @a)', 'sort(grep { $_ } @a)', 'sort(join("", @a), "a")', 'sort(values %h)', 'sort(%h)', 'sort(true, false)', 'sort(undef)', 'sort(undef, 1)',
         'sort(not 1)', 'sort(my @q = (2, 1))', 'sort(sub { 1 }, 2)', 'sort(\\@a)', 'sort([1], 2)', 'sort({}, 2)', 'sort(+{}, 2)', 'sort(__LINE__, 0)', 'sort(f)', 'sort(f())', 'sort(f() )', 'sort( @a)', 'sort(@a )',
         'sort(\n@a)', 'sort(@a,)', 'sort(,@a)', 'sort(ref $r, "A")', 'sort(length "abc", 1)', 'sort(defined $x, 1)', 'sort(reverse("ab"), "a")', 'sort(uc "b", "A")', 'sort(ucfirst "b", "A")', 'sort(quotemeta ".", "A")',
         'sort(chr 66, "A")', 'sort(ord "b", 1)', 'sort(pop @a, "z")', 'sort(shift @a, "z")', 'sort(exists $h{a}, 0)', 'sort(delete $h{a}, 0)', 'sort(scalar reverse("ab"), "a")', 'sort(sprintf("%s", "q"), "a")',
         'sort(substr("xb", 1), "a")', 'sort(index("xb", "b"), 0)', 'sort(join ",", 2, 1)', 'sort(push @a, 1)', 'sort(splice(@a, 0, 1), 0)', 'sort(keys(%h))', 'sort(keys %h, "0")', 'sort(values $hr->%*)',
         'sort(if 1)', 'sort(x 2)', 'sort("a" x 2, "a")', 'sort(("a") x 2)', 'sort(1, 2) x 2', 'sort say 1', 'sort(say(1), 0)', 'sort(return 1)', 'sort(die "x\\n")', 'sort($_) for 1', 'sort(a => 1)', 'sort(a, 1)', 'sort(a)', 'sort(a b)', 'sort(reverse)', 'sort(sort)', 'sort(keys)']
SAFTER = ['', '[0]', ' [0]', '->[0]', ', 9', ' x 2', ' . "x"', ' + 1', ' ? 1 : 2', ' if 1', ' or say "w"', ' == 3', '{a}', '()', ' for 1 .. 2']


def cases():
    n = 0
    for arr in ARRS:
        for after in AFTER:
            n += 1
            yield ('s%04d' % n, PRE + 'say scalar %s %s;\n' % (arr, after))
            if n % 3 == 0:
                yield ('v%04d' % n, PRE + 'my $v = scalar %s %s;\nsay $v;\n' % (arr, after))
    pre2 = PRE + 'my $x = 2; sub f(@l) { return reverse @l; }\n'
    for s in SORTS:
        n += 1
        yield ('j%04d' % n, pre2 + 'say join(",", %s);\n' % s)
        yield ('a%04d' % n, pre2 + 'my @o = %s;\nsay "@o";\n' % s)
        yield ('l%04d' % n, pre2 + 'for my $e (%s) { print $e, ";"; }\nprint "\\n";\n' % s)
    for s in SORTS[:8]:
        for after in SAFTER:
            n += 1
            yield ('t%04d' % n, pre2 + 'say %s%s;\n' % (s, after))
            yield ('u%04d' % n, pre2 + 'my @o = (%s%s);\nsay "@o";\n' % (s, after))
            yield ('w%04d' % n, pre2 + 'my $o = %s%s;\nsay $o;\n' % (s, after))
