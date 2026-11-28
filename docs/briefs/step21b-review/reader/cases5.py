# Programs by chance: opens (in place, in blocks, in subs, in closures), reads of every kind, stdin beside
# files, writes, closes, copies and drops of handles, failed opens and $!, try and catch, warnings and deaths.
# The generator keeps a loose account of what is open so that most programs run to their end.
import random, os
SUBS = '''sub slurp($n) { open(my $t, '<', $n) or die "slurp $n: $!\\n"; my @x = <$t>; close($t); return @x }
sub first($n) { open(my $t, '<', $n) or die "first $n: $!\\n"; my $x = <$t>; return $x }
sub put($n, $s) { open(my $t, '>', $n) or die "put $n: $!\\n"; print $t $s; return 1 }
sub app($n, $s) { open(my $t, '>>', $n) or die "app $n: $!\\n"; print $t $s; close($t); return 1 }
sub mk($m, $n) { my $t; if ($m eq 'r') { open($t, '<', $n) or die "mk $n: $!\\n"; } else { open($t, '>', $n) or die "mk $n: $!\\n"; } return $t }
sub line($h) { my $x = <$h>; return $x }
sub boom($m) { die $m }
my ($h0, $h1, $h2); my @keep; my $l; my @l; my $n = 0; my $tiny = 1e-200; my $f;
'''
RFILES = ['in.txt', 'nonl.txt', 'empty.txt', 'zero.txt']
def gen(seed):
    r = random.Random(seed)
    st = {}   # var -> (mode, file) or None when closed/undef
    wopen = set()
    out = []
    nw = 0
    def wfile():
        nonlocal nw
        if r.random() < 0.8:
            nw += 1; return f'w{nw}.txt'
        return r.choice(['w1.txt', 'in.txt', 'w2.txt'])
    for step in range(r.randint(4, 16)):
        h = r.choice(['$h0', '$h1', '$h2'])
        s = st.get(h)
        k = r.random()
        wild = r.random() < 0.08
        if not wild:
            # steer: a read wants a handle open for reading, a write one for writing, a close an open one
            if 0.36 <= k < 0.50 and not (s and s[0] == 'r'):
                hs = [x for x in st if st[x] and st[x][0] == 'r']
                if hs: h = r.choice(hs); s = st[h]
                else: k = r.choice([0.01, 0.25])
            if 0.50 <= k < 0.60 and not (s and s[0] == 'w'):
                hs = [x for x in st if st[x] and st[x][0] == 'w']
                if hs: h = r.choice(hs); s = st[h]
                else: k = 0.15
            if 0.60 <= k < 0.68 and not (s and s[0] in 'rw'):
                hs = [x for x in st if st[x] and st[x][0] in 'rw']
                if hs: h = r.choice(hs); s = st[h]
                else: k = 0.7
        if k < 0.14:
            fn = r.choice(RFILES + ['nope.txt']) if r.random() < 0.85 else wfile()
            style = r.choice(['die', 'dieb', 'if', 'plain', 'or2'])
            if style == 'die': out.append(f"open({h}, '<', '{fn}') or die \"open {fn}: $!\\n\";")
            elif style == 'dieb': out.append(f"open({h}, '<', '{fn}') or die \"open {fn}: $!\";")
            elif style == 'or2': out.append(f"open({h}, '<', '{fn}') || die \"open {fn}: \", \"$!\", \"\\n\";")
            elif style == 'if': out.append(f"if (open({h}, '<', '{fn}')) {{ print \"ok {fn}\\n\"; }} else {{ print \"not {fn}: $!\\n\"; }}")
            else: out.append(f"open({h}, '<', '{fn}');")
            st[h] = ('r', fn) if fn != 'nope.txt' else ('x', fn)
        elif k < 0.22:
            fn = wfile(); m = r.choice(['>', '>>'])
            out.append(f"open({h}, '{m}', '{fn}') or die \"open {fn}: $!\\n\";"); st[h] = ('w', fn)
        elif k < 0.30:
            fn = r.choice(RFILES)
            out.append(r.choice([
                f"{{ open(my $t, '<', '{fn}') or die \"n\\n\"; my $x = <$t>; print $x if defined($x); }}",
                f"{{ open(my $t, '<', '{fn}') or die \"n\\n\"; my $x = <$t>; print $x if defined($x); close($t); }}",
                f"{{ open(my $t, '<', '{fn}') or die \"n\\n\"; my @x = <$t>; print scalar(@x), \"\\n\"; }}",
                f"{{ open(my $t, '<', '{fn}') or die \"n\\n\"; print eof($t) ? \"E\\n\" : \"e\\n\"; }}",
                f"@l = slurp('{fn}'); print scalar(@l), \"\\n\";",
                f"$l = first('{fn}'); print defined($l) ? $l : \"U\\n\";",
                f"{h} = mk('r', '{fn}');",
                f"$l = line(mk('r', '{fn}')); print defined($l) ? $l : \"U\\n\";",
                f"for my $name ('{fn}', '{r.choice(RFILES)}') {{ open(my $t, '<', $name) or die \"n\\n\"; while (my $x = <$t>) {{ print $x; last if $n++ > 30; }} }}",
                f"$f = sub {{ open(my $t, '<', '{fn}') or die \"n\\n\"; my $x = <$t>; return $x }}; $l = $f->(); print defined($l) ? $l : \"U\\n\";",
                f"{{ open(my $t, '<', '{fn}') or die \"n\\n\"; $f = sub {{ my $x = <$t>; return $x }}; }} $l = $f->(); print defined($l) ? $l : \"U\\n\";",
                f"try {{ open(my $t, '<', '{fn}') or die \"n\\n\"; my $x = <$t>; die \"in try\\n\"; }} catch ($e) {{ print \"caught: $e\"; }}",
                f"@l = map {{ first($_) // 'U' }} ('{fn}', '{r.choice(RFILES)}'); print scalar(@l), \"\\n\";",
            ]))
            if 'mk(' in out[-1] and out[-1].startswith(h): st[h] = ('r', fn)
        elif k < 0.36:
            fn = wfile()
            out.append(r.choice([f"put('{fn}', \"p{step}\\n\");", f"app('{fn}', \"a{step}\\n\");", f"{{ open(my $t, '>', '{fn}') or die \"n\\n\"; print $t \"b{step}\\n\"; }}",
                                 f"{{ open(my $t, '>>', '{fn}') or die \"n\\n\"; say $t 'c{step}'; close($t); }}", f"{h} = mk('w', '{fn}');"]))
            if out[-1].startswith(h): st[h] = ('w', fn)
        elif k < 0.50:
            out.append(r.choice([f"$l = <{h}>; print defined($l) ? $l : \"U\\n\";", f"@l = <{h}>; print scalar(@l), \"\\n\";", f"while (my $x = <{h}>) {{ print \"[$x]\"; last if length($x) < 2; }}",
                                 f"print eof({h}) ? \"E\\n\" : \"e\\n\";", f"$l = line({h}); print defined($l) ? $l : \"U\\n\";", f"print <{h}>;", f"chomp(my $c{step} = <{h}> // ''); print \"<$c{step}>\";",
                                 f"while (!eof({h})) {{ $l = <{h}>; print \"($l)\"; }}", f"for my $x (<{h}>) {{ print \"-$x\"; }}"]))
        elif k < 0.60:
            out.append(r.choice([f"print {h} \"l{step}\\n\";", f"say {h} 'm{step}', {step};", f"printf {h} \"%03d|%s\\n\", {step}, 'q';", f"print {{ {h} }} 'r{step}', \"\\n\";", f"print {h} 'x' x 9000, \"\\n\";"]))
        elif k < 0.68:
            out.append(f"close({h});" if r.random() < 0.8 else f"close({h}) or die \"close: $!\\n\";"); st[h] = None
        elif k < 0.74:
            out.append(r.choice(["$l = <STDIN>; print defined($l) ? $l : \"U\\n\";", "@l = <STDIN>; print scalar(@l), \"\\n\";", "print eof(STDIN) ? \"E\\n\" : \"e\\n\";"]))
        elif k < 0.82:
            h2 = r.choice(['$h0', '$h1', '$h2'])
            c = r.choice([f"{h2} = {h};", f"{h} = undef;", f"push @keep, {h};", "@keep = ();", f"{h} = $keep[0] if @keep;", f"($h0, $h1) = ($h1, $h0);", f"print ref({h}), defined({h}) ? 'd' : 'u', \"\\n\";",
                          f"print {h} == {h2} ? \"same\\n\" : \"other\\n\" if defined({h}) && defined({h2});"])
            out.append(c)
            if c.startswith(f"{h2} = "): st[h2] = st.get(h)
            elif c.startswith(f"{h} = undef"): st[h] = None
            elif 'h0, $h1) =' in c: st['$h0'], st['$h1'] = st.get('$h1'), st.get('$h0')
            elif '$keep[0]' in c: st[h] = None
        elif k < 0.88:
            out.append(r.choice(["warn \"w\\n\";", "warn \"w\";", "try { die \"inner\" } catch ($e) { print \"caught: $e\"; }", "try { boom(\"b\\n\") } catch ($e) { print \"caught: $e\"; }",
                                 "try { open(my $t, '<', 'nope.txt') or die \"t: $!\\n\"; } catch ($e) { print \"caught: $e\"; }", "try { open(my $t, '<', 'nope.txt') or die \"t: $!\"; } catch ($e) { print \"caught: $e\"; }",
                                 "print STDERR \"err\\n\";", "{ my @junk = map { [$_, \"s$_\"] } 1 .. 40; }", "$n = $tiny * $tiny;", "$n = '1e-320' + 0;", "$n = 2 ** -1080;"]))
        else:
            fn = 'nope.txt'
            out.append(r.choice([f"if (!open({h}, '<', 'nope.txt')) {{ print \"failed: $!\\n\"; }}", f"if (!open({h}, '<', 'in.txt/x')) {{ my $why = $!; print \"failed: $why\\n\"; }}",
                                 f"unless (open({h}, '>', 'nodir/x')) {{ warn \"failed: $!\\n\"; }}", f"open({h}, '<', 'nope.txt'); print \"after: $!\\n\";"]))
            st[h] = ('x', fn)
    out.append(r.choice(['die "end\\n";', 'die "end";', 'exit 3;', 'exit;', 'say "done";', 'boom("in sub\\n");', 'boom("in sub");', 'warn "last"; say "done";', 'die "end: $!\\n";', 'die;', 'die "a", "b\\n";',
                         'try { die "end\\n" } catch ($e) { die "again: $e" }', 'close($h0); die "end";', '$h0 = undef; $h1 = undef; $h2 = undef; @keep = (); { my @junk = map { [$_] } 1 .. 30; } die "end";',
                         'die "end\\n";', 'die "end\\n";', 'my $z = <STDIN>; die "end";', 'print eof(STDIN) ? 1 : 0; die "end";']))
    return SUBS + '\n'.join(out) + '\n'
LO, HI = [int(x) for x in os.environ.get('SEEDS', '0-1500').split('-')]
U = "use v5.42;\nuse open ':std', ':encoding(UTF-8)';\n"
CASES = [{'p': gen(s), 'stdin': [b'', b's1\ns2\ns3\n', b's1'][s % 3], 'pre': U if s % 7 == 0 else 'use v5.42;\n'} for s in range(LO, HI)]
