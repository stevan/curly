#!/usr/bin/env python3
"""Step 21b's review, done by the builder as a pass of its own after the
build (no second agent could be started in the session): programs made by
rule and by chance, each run by perl 5.42 and by the compiler in a
directory of its own that holds the same files, and stdout, stderr and the
exit status each compared. A fault or a refusal is never a difference; a
program that runs to its end and differs in any of the three is WRONG.

    python3 docs/briefs/step21b-review/hunt.py              # all
    python3 docs/briefs/step21b-review/hunt.py contexts     # one family
    python3 docs/briefs/step21b-review/hunt.py --show NAME  # one program

The families:
  contexts   step 21a's 74 places a readline stands (its contexts.py), with
             `<$fh>` for `<STDIN>`, under four files, with `use open` and
             without
  values     a handle in every place a value stands
  print      what follows `print $x `, for a handle and for a number
  errno      `$!` and what a `die` exits with, after each thing that moves
             perl's errno
  bytes      files of bytes, read and written, with `use open` and without
  random     sequences of opens, reads, writes, closes, copies, messages
             and deaths, drawn by chance from a seed
"""
import concurrent.futures
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
PERL = os.environ.get('CURLY_PERL', '/opt/perl-5.42/bin/perl')
OPEN = "use open ':std', ':encoding(UTF-8)';\n"
FILES = {'in.txt': b'a\nb\nc\n', 'nonl.txt': b'x\ny', 'empty.txt': b'', 'zero.txt': b'1\n0', 'u.txt': 'caf\u00e9\n\u263a\n'.encode()}

sys.path.insert(0, os.path.join(HERE, '..', 'step21-review'))
from contexts import CONTEXTS  # noqa: E402


def contexts():
    for n, body in enumerate(CONTEXTS):
        if 'STDIN' not in body:
            continue
        body = body.replace('<STDIN>', '<$fh>').replace('eof(STDIN)', 'eof($fh)')
        for name in ('in.txt', 'nonl.txt', 'empty.txt', 'zero.txt'):
            for o, opened in enumerate(['', OPEN]):
                # (With `use open`, the two files that differ most.)
                if o and name in ('nonl.txt', 'empty.txt'):
                    continue
                yield f'contexts-{n}-{name[:-4]}-{o}', f"use v5.42;\n{opened}open(my $fh, '<', '{name}') or die \"no\\n\";\n{body}\n", b''


VALUES = [
    'say $fh ? "t" : "f";', 'say !$fh ? "t" : "f";', 'say defined($fh) ? 1 : 0;', 'say ref($fh);', 'say ref(\\$fh);',
    'say $fh == $g ? 1 : 0, $fh == $fh ? 1 : 0, $fh != $g ? 1 : 0;', 'say $fh eq $g ? 1 : 0;', 'say "$fh";', 'say $fh . "";',
    'say $fh + 0;', 'my @a = ($fh, $g); say scalar(@a); say ref($a[1]);', 'my %h = (k => $fh); say ref($h{k});', 'my %h = ($fh => 1);',
    'my %h; $h{$fh} = 1;', 'say length($fh);', 'say uc($fh);', 'my @s = sort ($fh, $g);', 'say join(",", $fh, $g);', 'my $s = $fh x 2;',
    'my $c = $fh; $c++;', 'say sprintf("%s", $fh);', 'say sprintf("%d", $fh);', 'chomp($fh); say ref($fh);', 'print $fh;', 'say $fh;',
    'print $fh, "x";', 'my $r = \\$fh; say ref($r), ref($r->$*);', 'my $r = [$fh]; my $l = <$r>;', 'say $fh->[0];', 'say $fh->{k};',
    'my @l = $fh->@*;', 'say $fh->$*;', '$fh->();', 'say $fh < $g ? 1 : 0;', 'say $fh <=> $g;', 'say $fh && 1;', 'say $fh || 2;',
    'say $fh // 3;', 'my $x = $fh ? "y" : "n"; say $x;', 'if ($fh) { say "if" }', 'unless ($fh) { say "unless" } else { say "else" }',
    'my @g = grep { $_ } ($fh, 0); say scalar(@g);', 'my @m = map { ref($_) } ($fh, 1, [2]); say "@m";', 'say scalar(@{[$fh]});',
    'my $n = 0; for my $h ($fh, $g) { my $l = <$h>; $n++ if defined $l } say $n;', 'try { die $fh } catch ($e) { say ref($e) }',
    'die $fh;', 'warn $fh;', 'die $fh, "x\\n";', 'exit $fh;', 'my $c = $fh; close($c); my $l = <$fh>;', 'my $c = $fh; close($c); say eof($g) ? 1 : 0;',
    'sub f($h) { return $h } say f($fh) == $fh ? 1 : 0;', 'sub f() { return $fh } my $l = <$fh>; my $h = f(); print scalar(1), $l;',
    'my $f = sub { my $l = <$fh>; return $l }; print $f->(), $f->();', 'my @hs = ($fh) x 2; say $hs[0] == $hs[1] ? 1 : 0;',
    'say substr($fh, 0, 4);', 'say index($fh, "GLOB");', 'say ord($fh);', 'say lc($fh) eq $fh ? 1 : 0;', 'say $fh ** 0;', 'say -$fh ? 1 : 0;',
    'my ($p, $q) = ($fh, $g); ($p, $q) = ($q, $p); my $l = <$p>; print $l;', 'my $l = <$fh> . <$g>; print $l;', 'say eof($fh) + eof($g);',
]


def values():
    for n, body in enumerate(VALUES):
        yield f'values-{n}', f"use v5.42;\nopen(my $fh, '<', 'in.txt') or die \"no\\n\";\nopen(my $g, '<', 'nonl.txt') or die \"no\\n\";\n{body}\nsay \"end\";\n", b''


AFTER = ['"a"', "'a'", '3', '.5', '-1', '- 1', '+1', '+ 1', '$y', '@a', '%h', 'f()', 'f', 'length("ab")', 'true', 'undef', '("a")', '("a") x 2',
         '(1 + 2) * 3', '!$y', '! $y', '!= 3', '\\@a', '[1]->[0]', 'x 2', 'eq "5"', 'if $y', 'unless $y', 'for 1 .. 2', 'and 1', '? 1 : 2', '?1:2',
         '/ 2', '* 2', '% 2', '< 2', '<< 1', '<<"E"', 'q(a)', 'qq(a)', 'qw(a b)', 'my $z = 4', 'join("-", 1, 2)', 'sort @a', 'map { $_ } @a',
         'sprintf("%d", 3)', '"a", "b"', '"a" . "b"', '"a" x 2', '$y, $y', '$y + 1', '$y x 2', '@a[0, 1]', '$a[0]', '$h{k}', 'scalar(@a)', '.. 3',
         '. "s"', '= 5', '== 5', ', "c"', '', '<$in>', '<STDIN>', '++', 'isa Foo', 'not 1', 'ref($y)', 'lc "A"', 'chr(65)', 'reverse "a", "b"']


def prints():
    for word in ('print', 'say'):
        for n, after in enumerate(AFTER):
            here = '\nx\nE' if 'E"' in after else ''
            for kind, first in (('handle', "open(my $x, '>', 'o.txt') or die \"no\\n\";"), ('number', 'my $x = 5;')):
                body = (f"use v5.42;\nsub f() {{ return \"F\" }}\nmy $y = 7; my @a = (1, 2); my %h = (k => 'v');\nopen(my $in, '<', 'in.txt') or die \"no\\n\";\n{first}\n"
                        f"{word} $x {after};{here}\nsay \"|\";\nif (ref($x)) {{ close($x); open($x, '<', 'o.txt') or die \"no\\n\"; print <$x>; }}\nsay \"end\";\n")
                yield f'print-{word}-{n}-{kind}', body, b's1\ns2\n'
    for n, form in enumerate(['print {$x} "a";', 'print {$x}"a";', 'print { $x } "a", "b";', 'print {$x} ("a");', 'print {$x};', 'print {$x}, "a";',
                              'print { $y ? $x : $x } "a";', 'print {$h{o}} "a";', 'print {$a[0]} "a";', 'print { f() } "a";', 'printf {$x} "%s-%s", 1, 2;',
                              'say {$x} "a" if $y;', 'print {$x} "a" for 1 .. 2;', 'print {$x} <$in>;', 'print($x "a");', 'print {"o"} "a";', 'print {$y} "a";',
                              'print {*STDOUT} "a";', 'print {STDOUT} "a";', 'print STDOUT $x "a";', 'printf $x "%s\\n", "a";', 'printf $x ("%s\\n", "a");',
                              'print $x "a" x 3, "\\n";', 'say $x 1 + 1;', 'say $x 1, 2 if $y;', 'my $r = \\$x; print {$r->$*} "a";', 'print {$x} {a => 1}->{a};']):
        body = (f"use v5.42;\nmy $y = 7;\nopen(my $in, '<', 'in.txt') or die \"no\\n\";\nopen(my $x, '>', 'o.txt') or die \"no\\n\";\nmy %h = (o => $x); my @a = ($x);\nsub f() {{ return $x }}\n"
                f"{form}\nsay \"|\";\nclose($x); open($x, '<', 'o.txt') or die \"no\\n\"; print <$x>;\nsay \"end\";\n")
        yield f'print-block-{n}', body, b''


MOVES = ["open(my $a1, '<', 'in.txt');", "open(my $a2, '<', 'nope.txt');", "open(my $a3, '>', 'o.txt');", "open(my $a4, '>>', 'o.txt');",
         "open(my $a5, '<', 'in.txt'); my $l5 = <$a5>;", "open(my $a6, '<', 'in.txt'); my @l6 = <$a6>;", "open(my $a7, '<', 'in.txt'); while (my $l = <$a7>) { }",
         "open(my $a8, '<', 'in.txt'); my $e8 = eof($a8);", "open(my $a9, '<', 'empty.txt'); my $e9 = eof($a9); my $l9 = <$a9>;",
         "open(my $b1, '<', 'empty.txt'); my $l = <$b1>;", "open(my $b2, '<', 'nonl.txt'); my $l = <$b2>; $l = <$b2>;", "open(my $b3, '<', 'in.txt'); close($b3);",
         'my $s1 = <STDIN>;', 'my @s2 = <STDIN>;', 'my $e3 = eof(STDIN);', 'my $t1 = "1e-400" + 0;', 'my $t2 = 2 ** -2000;',
         "open(my $b4, '>', 'o2.txt'); print $b4 'x' x 10000; close($b4);", 'try { die "d\\n" } catch ($e) { }', 'my @so = sort { $a <=> $b } 3, 1, 2;',
         'my $f1 = sprintf("%.3f %s %d", 1.5, "a", 3);', 'my $n1 = "12" + "3.5";', 'my %hh = (a => 1); my @k = sort keys %hh;', "open(my $b5, '<', 'no/dir/x');",
         "open(my $b6, '>', 'no/dir/x');", "open(my $b7, '<', 'in.txt'); my $l = <$b7>; open($b7, '<', 'nope.txt');"]
ENDS = ['die "x\\n";', 'say "[$!]";', 'my $w = $!; say $w ? "t" : "f";', 'die "x: $!\\n";', 'exit 0;', 'warn "w\\n"; say length("$!");', 'die "x";']


def errno():
    k = 0
    for i, first in enumerate(MOVES):
        for j, b in enumerate(MOVES + ['']):
            # (Every pair with every end would be 4,000 programs: each move
            # alone, and after a fifth of the others, with a third of the ends.)
            if first == b or (b and (i + j) % 5 != 0):
                continue
            second = re.sub(r'\$l\b', '$m', b)
            for e, end in enumerate(ENDS):
                if b and (k + e) % 3 != 0:
                    continue
                yield f'errno-{i}-{j}-{e}', f"use v5.42;\n{first}\n{second}\n{end}\n", b'in\n'
            k += 1


def bytes_():
    datas = {'latin': b'caf\xe9\n', 'utf8': 'caf\u00e9 \u263a\n'.encode(), 'cut': b'ok\na\xc3', 'crlf': b'a\r\nb\r', 'nul': b'a\x00b\n', 'bom': b'\xef\xbb\xbfx\n',
             'high': b'\xff\xfe\n', 'surrogate': b'\xed\xa0\x80\n', 'empty': b'', 'long': b'x' * 9000 + b'\ny' * 3}
    bodies = ['my $l = <$fh>; say defined $l ? length($l) : "u";', 'my @l = <$fh>; say scalar(@l); for my $x (@l) { say length($x), ":", ord($x) }',
              "while (my $l = <$fh>) { chomp($l); say length($l) }", "my $l = <$fh>; open(my $o, '>', 'o.txt') or die \"no\\n\"; print $o $l; close($o); open(my $back, '<', 'o.txt') or die \"no\\n\"; my $m = <$back>; say defined $m && defined $l && $m eq $l ? 'same' : 'differ';",
              "open(my $o, '>', 'o.txt') or die \"no\\n\"; print $o chr(233), chr(65), \"\\n\"; close($o); open(my $back, '<', 'o.txt') or die \"no\\n\"; my $m = <$back>; say length($m);",
              "open(my $o, '>', 'o.txt') or die \"no\\n\"; print $o chr(9786); close($o); say 'written';", "open(my $o, '>', 'o.txt') or die \"no\\n\"; say $o chr(0xFFFF); say 'written';",
              'my $l = <$fh>; print $l if defined $l;']
    for name, data in datas.items():
        for n, body in enumerate(bodies):
            for o, opened in enumerate(['', OPEN]):
                yield f'bytes-{name}-{n}-{o}', f"use v5.42;\n{opened}open(my $fh, '<', 'd.txt') or die \"no\\n\";\n{body}\n", b'', {'d.txt': data}


def randoms(count=260):
    for seed in range(count):
        rnd = random.Random(seed)
        lines, live, n = ['use v5.42;'], {}, 0     # live: var -> 'r' | 'w' | 'c'
        for _ in range(rnd.randint(4, 11)):
            n += 1
            roll = rnd.random()
            var = rnd.choice(list(live)) if live else None
            readers = [v for v, m in live.items() if m == 'r']
            writers = [v for v, m in live.items() if m == 'w']
            if roll < 0.22 or not live:
                new = f'h{n}' if rnd.random() < 0.7 or not live else None
                target = f'my ${new}' if new else f'${var}'
                mode = rnd.choice(['<', '<', '<', '>', '>>'])
                name = rnd.choice(['in.txt', 'nonl.txt', 'empty.txt', 'nope.txt']) if mode == '<' else rnd.choice(['o1.txt', 'o2.txt'])
                how = rnd.choice([';', ' or die "no ' + name + ': $!\\n";', ' or die "no ' + name + ': $!";', ' || die "no\\n";'])
                lines.append(f"open({target}, '{mode}', '{name}'){how}")
                live[new or var] = 'c' if name == 'nope.txt' else ('r' if mode == '<' else 'w')
            elif roll < 0.40 and (readers or rnd.random() < 0.1):
                v = rnd.choice(readers) if readers else var
                lines.append(rnd.choice([f'{{ my $l = <${v}>; print defined $l ? "[$l]" : "[u]"; }}', f'{{ my @a = <${v}>; print scalar(@a), "\\n"; }}',
                                         f'while (my $l = <${v}>) {{ print "w[$l]" }}', f'print eof(${v}) ? "E" : "M";', f'{{ my ($p, $q) = <${v}>; print defined $q ? "2" : "1"; }}']))
            elif roll < 0.52 and (writers or rnd.random() < 0.1):
                v = rnd.choice(writers) if writers else var
                lines.append(rnd.choice([f'print ${v} "t{n}\\n";', f'say ${v} "s", {n};', f'printf ${v} "%03d\\n", {n};', f'print {{${v}}} "b{n}\\n";', f'say {{ ${v} }} {n} + 1;']))
            elif roll < 0.62:
                lines.append(rnd.choice([f'close(${var});', f'close ${var};', f'close(${var}) or die "close: $!\\n";']))
                if live.get(var) in ('r', 'w'):
                    live[var] = 'c'
            elif roll < 0.68:
                lines.append(f'my $c{n} = ${var};')
                live[f'c{n}'] = live[var]
            elif roll < 0.74:
                lines.append(rnd.choice(['{ my $s = <STDIN>; print defined $s ? "s[$s]" : "s[u]"; }', 'print eof(STDIN) ? "SE" : "SM";', '{ my @s = <STDIN>; print scalar(@s); }']))
            elif roll < 0.82:
                lines.append(rnd.choice([f'warn "w{n}";', f'warn "w{n}\\n";', f'try {{ die "d{n}" }} catch ($e) {{ print "c:$e" }}', f'try {{ die "d{n}\\n" }} catch ($e) {{ print "c:$e" }}']))
            elif roll < 0.87:
                lines.append(rnd.choice(['print "[$!]\\n";', '{ my $w = $!; print "e:", ($w ? 1 : 0), "\\n"; }', '{ my $s = "1e-400"; my $t = $s + 0; }']))
            elif roll < 0.92:
                lines.append(f'${var} = undef;')
                live.pop(var)
            else:
                name = rnd.choice(['in.txt', 'o1.txt'])
                lines.append(rnd.choice([f"{{ open(my $t, '<', '{name}'); my $l = <$t>; print defined $l ? 'T' : 'U'; }}", f"{{ open(my $t, '>>', 'o1.txt'); print $t 'scoped'; }}",
                                         f"sub s{n}() {{ my $t; return 0 unless open($t, '<', '{name}'); my @l = <$t>; return scalar(@l) }} print s{n}();"]))
        for v, m in live.items():
            if m == 'w' and rnd.random() < 0.5:
                lines.append(f'close(${v});')
        # What the files hold at the end is part of what a program did.
        ending = rnd.choice(['', '', 'die "end\\n";', 'die "end";', 'exit 3;', 'warn "last";'])
        if not ending.startswith(('die', 'exit')):
            lines.append("for my $name ('o1.txt', 'o2.txt') { if (open(my $z, '<', $name)) { print \"$name: \", <$z>; close($z); } }")
        lines += [ending, '']
        yield f'random-{seed}', '\n'.join(lines), b's1\ns2'


FAMILIES = {'contexts': contexts, 'values': values, 'print': prints, 'errno': errno, 'bytes': bytes_, 'random': randoms}


def run(argv, stdin, cwd):
    try:
        r = subprocess.run(argv, input=stdin, capture_output=True, timeout=60, cwd=cwd, env={'PATH': '/usr/bin:/bin', 'CURLY_GC_STRESS': '1', 'CURLY_GC_POISON': '1', 'PERL_HASH_SEED': '1'})
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None


def judge(case, base):
    name, code, stdin = case[:3]
    files = {**FILES, **(case[3] if len(case) > 3 else {})}
    made = {}
    for who in ('perl', 'ours'):
        d = os.path.join(base, f'{name}.{who}')
        os.makedirs(d)
        for f, data in files.items():
            open(os.path.join(d, f), 'wb').write(data)
        open(os.path.join(d, 'p.pl'), 'w', encoding='utf-8').write(code)
        made[who] = d
    exe = os.path.join(base, name + '.bin')
    c = subprocess.run(['node', os.path.join(ROOT, 'bin/curlyc.ts'), '-o', exe, 'p.pl'], capture_output=True, text=True, cwd=made['ours'])
    try:
        if c.returncode == 1:
            return 'refused', c.stderr.strip()
        if c.returncode != 0:
            return 'BROKE', c.stderr.strip()
        perl = run([PERL, 'p.pl'], stdin, made['perl'])
        ours = run([exe], stdin, made['ours'])
        if perl is None or ours is None:
            return 'no end', f'perl {perl}, ours {ours}'
        if ours[0] == 2 and ours[2].startswith(b'internal: '):
            return 'BROKE', ours[2].decode()
        cut = ours[2].rfind(b'fault: ')
        if ours[0] == 1 and cut >= 0:
            if perl[1].startswith(ours[1]) and perl[2].startswith(ours[2][:cut]):
                return 'fault', ours[2][cut:].decode('utf-8', 'replace').strip()
            return 'WRONG', f'it faults after writing what perl does not\n  perl: {perl}\n  ours: {ours}'
        if perl == ours:
            return 'same', ''
        return 'WRONG', f'\n  perl: {perl}\n  ours: {ours}'
    finally:
        for d in made.values():
            shutil.rmtree(d, ignore_errors=True)
        for f in (exe, exe + '.c', exe + '.rt.o'):
            if os.path.exists(f):
                os.unlink(f)


def main(argv):
    show = argv[1] if argv[:1] == ['--show'] else None
    wanted = [a for a in argv if a in FAMILIES] or list(FAMILIES)
    cases = [c for f in wanted for c in FAMILIES[f]()]
    if show:
        cases = [c for f in FAMILIES for c in FAMILIES[f]() if c[0] == show]
    counts, faults = {}, {}
    with tempfile.TemporaryDirectory() as base:
        os.environ['CURLY_RT_OBJ'] = os.path.join(base, 'rt.o')
        judge(('warm', 'use v5.42;\nsay 1;\n', b''), base)
        with concurrent.futures.ThreadPoolExecutor(int(os.environ.get('JOBS', '2'))) as pool:
            for case, (verdict, why) in zip(cases, pool.map(lambda c: judge(c, base), cases)):
                family = case[0].split('-')[0]
                counts[(family, verdict)] = counts.get((family, verdict), 0) + 1
                if verdict == 'fault':
                    faults[why.split(' at p.pl')[0]] = faults.get(why.split(' at p.pl')[0], 0) + 1
                if verdict in ('WRONG', 'BROKE', 'no end') or show:
                    print(f'{verdict}: {case[0]}\n{case[1]}\n  {why}\n')
    for family in wanted:
        print(family + ':', ', '.join(f'{n} {v}' for (f, v), n in sorted(counts.items()) if f == family))
    print('the faults:', ', '.join(f'{n} {w}' for w, n in sorted(faults.items(), key=lambda x: -x[1])))
    return 1 if any(v in ('WRONG', 'BROKE') for _, v in counts) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
