#!/usr/bin/env python3
# Step 22's evidence for D203: what `hex` and `oct` take in silence. Every
# string of up to N characters (default 4) over a 21-letter alphabet is
# given to perl's hex and oct, with a warning noted; the model below, which
# runtime/num.c is written from, must give perl's value wherever it takes a
# string, and only where perl is silent. It counts where the model faults
# and perl is silent too: oct's silent stops, D203's strictness.
#
#     python3 docs/briefs/step22-hexoct.py 4
#     (204205 strings: model agrees with perl on 21749, faults where perl is
#     silent on 130709, differs on 0)
import itertools, os, subprocess, sys

ALPHA = ['0','1','7','8','9','a','f','g','x','X','b','B','o','O','_',' ','\t','-','+','.','e']
def strings(n):
    for k in range(n+1):
        for t in itertools.product(ALPHA, repeat=k):
            yield ''.join(t)
DIG = {16: '0123456789abcdefABCDEF', 8: '01234567', 2: '01'}
def digits(s, base):
    # perl: an optional leading '_' (after the prefix), digits with single underscores between
    if s == '': return 0
    v = 0; prev_us = False
    if s.startswith('_'):
        s = s[1:]; prev_us = True
        if s == '': return None
    for i, ch in enumerate(s):
        if ch == '_':
            if prev_us or i == len(s) - 1: return None
            prev_us = True; continue
        prev_us = False
        if ch not in DIG[base]: return None
        v = v * base + int(ch, 16)
    return v
def model(fn, s):
    if fn == 'hex':
        t = s
        if t[:2] in ('0x', '0X'): t = t[2:]
        elif t[:1] in ('x', 'X'): t = t[1:]
        v = digits(t, 16)
    else:
        t = s.lstrip(' \t\n\r\f\v')
        p = t[:2].lower()
        if p in ('0x', '0b', '0o'): base = {'x':16,'b':2,'o':8}[p[1]]; t = t[2:]
        elif t[:1].lower() in ('x','b','o'): base = {'x':16,'b':2,'o':8}[t[0].lower()]; t = t[1:]
        else: base = 8
        v = digits(t, base)
    if v is None or v > 0xFFFFFFFF: return None
    return v
n = int(sys.argv[1]) if len(sys.argv) > 1 else 4; STRICT = len(sys.argv) > 2
ss = list(strings(n))
perl = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', r'''use v5.42; my $w; $SIG{__WARN__} = sub { $w = 1 }; while (my $l = <STDIN>) { chomp $l; my $s = $l =~ s/\\t/\t/gr; for my $f ("hex", "oct") { $w = 0; my $v = $f eq "hex" ? hex($s) : oct($s); print "$v $w "; } print "\n"; }'''],
    input=''.join(s.replace('\t','\\t') + '\n' for s in ss), capture_output=True, text=True).stdout.splitlines()
bad = strict = agree = 0
for s, line in zip(ss, perl):
    f = line.split()
    for k, fn in enumerate(('hex', 'oct')):
        pv, pw = f[2*k], f[2*k+1]
        m = model(fn, s)
        if m is None:
            if pw == "0":
                strict += 1
                if fn == "hex" and STRICT: print("STRICT", repr(s), pv)
        else:
            if pw != '0' or str(m) != pv:
                bad += 1
                if bad < 20: print('DIFF', fn, repr(s), 'model', m, 'perl', pv, pw)
            else: agree += 1
print(f'{len(ss)} strings: model agrees with perl on {agree}, faults where perl is silent on {strict}, differs on {bad}')
