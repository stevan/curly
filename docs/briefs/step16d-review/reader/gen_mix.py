"""Random programs over the new statements and the lone range (D251, D252,
D253, D259): loops over ranges whose ends name arrays, hashes, scalars and
references, with blocks that change them, by name, through references, in
subs and in closures made in the loop; `$#a = N`, `undef`, `do { } while`
between and inside. Every loop is counted by something no fault touches
(T131)."""
import random

ENDS = ['$#a', '$#b', 'scalar(@a)', 'scalar @b', '@a', '$n', '$m', '$n + 1', '$r->$#*', '$#{$r}', 'scalar($r->@*)', 'keys %h', 'scalar(%h)', '$a[0]', '$a[1]', '$b[-1]', '$h{n}', '$r->[0]',
        'hi()', 'cnt()', '2', '3', '$s->$*', '${$s}', 'pop(@b) // 0', '$#a + $#b', '$t->{k}->$#*', '$#{$t->{k}}']
LOWS = ['0', '1', '$n - 2', '$m', '-1', '$a[0]', 'lo()', '$#b']
LISTS = ['@a', '@b', '$r->@*', 'values %h', '0 .. $#a, 0', 'reverse 0 .. $#a', '@a[0 .. $#a]', '(0 .. $#a)', '+(0 .. $#b)', 'map { $_ } 0 .. $#a', 'sort { $a <=> $b } 0 .. $#b', 'grep { true } 0 .. $n', 'sort keys %h']
CHANGES = ['push @a, $v;', 'pop @a;', 'shift @a;', 'unshift @b, 7;', 'splice(@a, 0, 1);', '$#a = 1;', '$#a = $#a + 1;', '$#b = -1;', 'undef @a;', 'undef @b;', '@a = (1, 2, 3, 4);', '@b = ();',
           '$a[0] = 9;', '$a[$v] = $v if $v >= 0;', '$b[5] = 1;', 'undef $a[1];', '$n++;', '$n = 0;', '$m = 4;', 'undef $n;', '$n = 2;', '$h{"k$v"} = 1;', 'delete $h{n};', 'undef %h;', '%h = (n => 1);', '$h{n} = 3;',
           'push $r->@*, 1;', '$r = [1];', 'undef $r;', '$r->$#* = 0;', '$#{$r} = 3;', '$r->[0] = 2;', 'undef $r->@*;', '$s->$* = 1;', '${$s} = 3;', '$t->{k} = [];', 'push $t->{k}->@*, 1;', 'undef $t->{k};', '$#{$t->{k}} = 2;',
           'chg();', 'chr2();', '$cl->();', 'push @subs, sub { push @a, $v; return $v + scalar(@a); };', 'push @subs, sub { $n++; return "$v/$n"; };', 'push @subs, sub { return $v; };',
           'push @refs, \\@a;', 'my $al = \\@b; push $al->@*, $v;', '$rr->$#* = 1;', 'undef $rr->@*;', 'push $rr->@*, 5;']
READS = ['say "v$v";', 'say "a@a";', 'say "n", $n // "u";', 'say "b", scalar(@b);', 'say "h", join(",", sort keys %h);', 'say "r", defined $r ? scalar($r->@*) : "u";', 'say "c$c";']

PRE = '''my @a = (1, 2, 3); my @b = (2, 1); my $n = 3; my $m = 1; my %h = (n => 2, x => 1); my $r = [3, 2, 1]; my $x = 2; my $s = \\$x; my $t = { k => [1, 2] }; my $rr = \\@a;
my @subs; my @refs; my $c = 0; my $calls = 0;
sub hi() { $calls++; return scalar(@a); } sub lo() { $calls++; return 0; } sub cnt() { return $n // 0; }
sub chg() { push @a, 8; $n = 5; return; } sub chr2() { $#b = 0; $h{z} = 1; return; }
my $cl = sub { shift @a; $m++; return; };
'''


def block(rnd, depth, var):
    out = []
    for _ in range(rnd.randrange(1, 4)):
        k = rnd.randrange(10)
        if k < 5:
            out.append(rnd.choice(CHANGES).replace('$v', var))
        elif k < 7:
            out.append(rnd.choice(READS).replace('$v', var))
        elif k == 7 and depth < 2:
            out.append(loop(rnd, depth + 1))
        elif k == 8:
            out.append(rnd.choice(['last if $c > 6;', 'next if $c % 2;', 'last OUT if $c > 9;', 'next OUT if $c == 3;', 'return if $c > 12;', '$c > 20 and last;', '$c < 30 or next;']))
        else:
            out.append('{ my $w = 0; do { $w++; %s } while ($w < 2); }' % rnd.choice(CHANGES).replace('$v', var))
    return ' '.join(out)


def loop(rnd, depth):
    var = '$' + 'ijk'[depth]
    k = rnd.randrange(12)
    if k < 7:
        head = 'for my %s (%s .. %s)' % (var, rnd.choice(LOWS), rnd.choice(ENDS))
    elif k < 9:
        head = 'for my %s (%s)' % (var, rnd.choice(LISTS))
    elif k == 9:
        return '$_ > 100 or $c++ for %s .. %s;' % (rnd.choice(LOWS), rnd.choice(ENDS))
    elif k == 10:
        return 'push @subs, map { my $q = $_; sub { return $q; } } %s .. %s;' % (rnd.choice(LOWS), rnd.choice(ENDS))
    else:
        head = 'for (%s .. %s)' % (rnd.choice(LOWS), rnd.choice(ENDS))
        var = '$_'
    body = block(rnd, depth, var)
    body = body.replace('sub { push @a, $_; return $_ + scalar(@a); }', 'sub { return 0; }').replace('sub { $n++; return "$_/$n"; }', 'sub { return 1; }').replace('sub { return $_; }', 'sub { return 2; }')
    return '%s { $c++; last if $c > 40; %s }' % (head, body)


def cases():
    rnd = random.Random(259)
    for n in range(900):
        parts = []
        for _ in range(rnd.randrange(1, 4)):
            if rnd.randrange(3):
                made = loop(rnd, 0)
                parts.append('OUT: ' + made if made.startswith('for') else made)
            else:
                parts.append(rnd.choice(CHANGES).replace('$v', '$m'))
        body = '\n'.join(parts)
        tail = 'say "end a@a b@b n", $n // "u", " m$m c$c calls$calls h", join(",", sort keys %h), " r", defined $r ? "@{$r}" : "u", " x$x";\nsay join(",", map { $_->() } @subs);\nsay "a@a";\n'
        if 'return' in body:
            yield ('x%03d' % n, PRE + 'sub run() {\n' + body + '\nreturn; }\nrun();\n' + tail)
        else:
            yield ('x%03d' % n, PRE + body + '\n' + tail)
