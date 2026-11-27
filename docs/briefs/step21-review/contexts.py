#!/usr/bin/env python3
"""Step 21a's review, done by the builder as a pass of its own (no second
agent could be started in the session that built it): every place a
readline can stand, each under several inputs, run by perl 5.42 and by the
compiler, and every program the compiler takes and runs to the end held to
perl's stdout and exit status. A fault or a refusal is never a difference.

    python3 docs/briefs/step21-review/contexts.py            # all
    python3 docs/briefs/step21-review/contexts.py --show N   # one program

It prints each difference, then a count of each verdict.
"""
import os
import subprocess
import sys
import tempfile

PERL = os.environ.get('CURLY_PERL', '/opt/perl-5.42/bin/perl')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
OPEN = "use open ':std', ':encoding(UTF-8)';\n"

# Each a program body. `S` is stdin under several inputs.
CONTEXTS = [
    'my $x = <STDIN>; print defined $x ? "[$x]" : "undef";',
    'my $x = (<STDIN>); print "[$x]";',
    'my ($x) = <STDIN>; my $y = <STDIN>; print "[$x]", defined $y ? 1 : 0;',
    'my @a = <STDIN>; say scalar(@a);',
    'my @a = (<STDIN>, "end"); say scalar(@a), $a[-1];',
    'my @a = (scalar(@ARGV), <STDIN>); say scalar(@a);',
    'say scalar(my @a = <STDIN>);',
    'my $n = () = <STDIN>; say $n;',
    'print <STDIN>;',
    'say <STDIN> . "!";',
    'say length <STDIN>;',
    'say length(<STDIN>) // "u";',
    'say uc <STDIN>;',
    'my $s = <STDIN> x 3; print $s;',
    'my @l = (<STDIN>) x 2; say scalar(@l);',
    'my @l = ((<STDIN>) x 2, 1); say scalar(@l);',
    'say join("|", <STDIN>);',
    'say join(<STDIN>, "a", "b");',
    'my @r = reverse <STDIN>; print @r;',
    'my @s = sort <STDIN>; print @s;',
    'my @m = map { "<$_>" } <STDIN>; print @m;',
    'my @g = grep { length($_) > 2 } <STDIN>; say scalar(@g);',
    'my @m = map { <STDIN> } 1 .. 2; say scalar(@m);',
    'my @g = grep { <STDIN> } 1 .. 3; say "@g";',
    'my @s = sort { <STDIN> cmp <STDIN> } 1 .. 3; say "@s";',
    'for my $l (<STDIN>) { print "[$l]" }',
    'for (<STDIN>) { print "($_)" }',
    'print "[$_]" for <STDIN>;',
    'while (my $l = <STDIN>) { print "[$l]" }',
    'my $l; while ($l = <STDIN>) { print "[$l]" }',
    'my @a; while ($a[0] = <STDIN>) { print "[$a[0]]" }',
    'my %h; while ($h{k} = <STDIN>) { print "[$h{k}]" }',
    'my $r = []; while ($r->[0] = <STDIN>) { print "[$r->[0]]" }',
    'while ((my $l = +<STDIN>)) { print "[$l]" }',
    'while (my $l = <STDIN>) { last if $l eq "b\\n"; print $l } print "rest:", <STDIN>;',
    'if (my $l = <STDIN>) { print "t[$l]" } else { print "f" }',
    'my $l = <STDIN> // "u"; print $l;',
    'my $l = <STDIN> || "f"; print $l;',
    'my $l = <STDIN> && "t"; print $l;',
    'my $l = <STDIN> ? "t" : "f"; print $l;',
    'print <STDIN> ? "t" : "f";',
    'my @a = (0) x 3; $a[1] = <STDIN>; print $a[1] // "u";',
    'my %h; $h{k} = <STDIN>; print exists $h{k} ? 1 : 0;',
    'my %h; $h{k} .= <STDIN>; print $h{k};',
    'my @a; push @a, <STDIN>; say scalar(@a);',
    'my @a = (1); unshift @a, <STDIN>; say scalar(@a);',
    'my $r = [<STDIN>]; say scalar(@$r);',
    'my $r = [<STDIN>]; say scalar($r->@*);',
    'my %h = map { ($_ => 1) } <STDIN>; say scalar(keys %h);',
    'sub f(@a) { return scalar(@a) } say f(<STDIN>);',
    'sub f($x, @a) { return $x } print f(<STDIN>);',
    'sub f($x) { return $x } print f(scalar(@ARGV) ? 1 : <STDIN>);',
    'sub g() { return <STDIN> } my @l = g(); say scalar(@l);',
    'sub g() { <STDIN> } my @l = g(); say scalar(@l);',
    'sub g() { return <STDIN> } my $l = g(); print $l;',
    'my $f = sub { <STDIN> }; my @l = $f->(); say scalar(@l);',
    'my $x = do_it(); sub do_it() { my $l = <STDIN>; return $l } print $x;',
    'my $c = 0; $c++ while defined(my $l = <STDIN>) && $c < 9; say $c;',
    'my $t = ""; $t .= $_ for <STDIN>; print $t;',
    'chomp(my $l = <STDIN>); print "[$l]";',
    'my @a = (<STDIN>)[0, 1]; print @a;',
    'my $x = (<STDIN>)[-1]; print $x;',
    'my @a = (<STDIN>)[1 .. 2]; say scalar(@a);',
    'say eof(STDIN) ? 1 : 0; my $x = <STDIN>; say eof(STDIN) ? 1 : 0;',
    'my $x = <STDIN>; my $y = <STDIN>; print $y . $x;',
    'print <STDIN> . <STDIN>;',
    'say <STDIN> eq <STDIN> ? "same" : "diff";',
    'my %h; my $k = "a"; $h{$k} = <STDIN>; print $h{a};',
    'my @a = ("x"); my $i = 0; $a[$i] = <STDIN>; print $a[0];',
    'try { my $l = <STDIN>; die $l } catch ($e) { print "caught $e" }',
    'my $n = 0; until (eof(STDIN)) { my $l = <STDIN>; $n++ } say $n;',
    'my $total = 0; while (my $l = <STDIN>) { $total += length $l } say $total;',
    'my @l = <STDIN>; my %count; $count{$_}++ for @l; say join(",", map { "$_=$count{$_}" } sort keys %count) =~ tr/\\n//dr;',
]

INPUTS = [b'', b'a\nb\n', b'a\nb\n0', b'0\n', b'0', b'b\na\nc\n\n', b'x y\n\n\n']


def run(argv, stdin, cwd):
    try:
        r = subprocess.run(argv, input=stdin, capture_output=True, timeout=10, cwd=cwd)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None


def main(argv):
    show = int(argv[1]) if argv[:1] == ['--show'] else None
    counts = {}
    with tempfile.TemporaryDirectory() as d:
        os.environ['CURLY_RT_OBJ'] = os.path.join(d, 'rt.o')
        for n, body in enumerate(CONTEXTS):
            if show is not None and n != show:
                continue
            for o, opened in enumerate(['', OPEN]):
                src = os.path.join(d, f'p{n}_{o}.pl')
                code = 'use v5.42;\n' + opened + body + '\n'
                open(src, 'w').write(code)
                exe = src[:-3]
                c = subprocess.run(['node', os.path.join(ROOT, 'bin/curlyc.ts'), '-o', exe, src], capture_output=True, text=True)
                for data in INPUTS:
                    perl = run([PERL, src], data, d)
                    if c.returncode == 1:
                        verdict = 'refused'
                    elif c.returncode != 0:
                        verdict = 'BROKE'
                    else:
                        ours = run([exe], data, d)
                        if ours is None or perl is None:
                            verdict = 'no end'
                        elif ours[0] == 1 and ours[2].startswith(b'fault: '):
                            verdict = 'fault' if perl[1].startswith(ours[1]) else 'WRONG'
                        elif perl[2] and ours[0] == perl[0] and ours[1] == perl[1]:
                            verdict = 'same, perl warned'
                        elif perl[2]:
                            verdict = 'WRONG (perl warned)'
                        elif ours[0] == perl[0] and ours[1] == perl[1] and ours[2] == perl[2]:
                            verdict = 'same'
                        else:
                            verdict = 'WRONG'
                    counts[verdict] = counts.get(verdict, 0) + 1
                    if verdict.startswith('WRONG') or verdict == 'BROKE' or show is not None:
                        print(f'{verdict}: #{n} {code!r} stdin={data!r}\n  perl: {perl}\n  ours: {c.stderr.strip() if c.returncode else run([exe], data, d)}')
    print(counts)


if __name__ == '__main__':
    main(sys.argv)
