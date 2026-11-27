#!/usr/bin/env python3
"""The review of the freeze's exception for a lone range (D259), as a
separate pass by the builder: random loops over one range whose ends name
arrays, hashes, scalars, references and subs, with blocks that change all
of them and subs that capture the loop's variable; and the same loops with a
second item in the list, which must stay frozen. Each compiled and run, and
run by perl: a program the language runs must print what perl prints, one it
faults must have printed the start of it.

    python3 docs/briefs/step16d-review/part3.py [COUNT] [SEED]
"""
import concurrent.futures
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from part1 import run  # noqa: E402

ENDS = ['0', '1', '$#a', 'scalar(@a)', '$n', '$a[0]', 'scalar(keys %h)', '$#{$r}', 'f()', '$n - 1', '-1']
BODY = ['push @a, $i;', 'shift @a;', '$a[$i] = $i * 2;', '@a = (7);', '$#a = 0;', '$n = 1;', '$n++;', '$h{"k$i"} = 1;', 'delete $h{x};',
        'push $r->@*, 1;', '$r = [];', 'push @s, sub { $i };', 'g($i);', 'say $i;', 'say "@a";', 'last if $i > 6;', 'next if $i == 1;']


def program(rnd):
    lo, hi = rnd.choice(ENDS), rnd.choice(ENDS)
    body = ' '.join(rnd.choice(BODY) for _ in range(rnd.randrange(1, 5)))
    extra = rnd.random() < 0.25
    items = f'{lo} .. {hi}' + (', 9' if extra else '')
    return f'''use v5.42;
my @a = (3, 1, 2);
my %h = (x => 1, y => 2);
my $r = [5, 6];
my $n = 2;
my @s;
sub f() {{ return scalar(@a); }}
sub g($k) {{ push @a, $k; $n = $k; return; }}
my $count = 0;
for my $i ({items}) {{
    $count++;
    last if $count > 20;
    {body}
}}
say "$count ", scalar(@a), " $n ", scalar(keys %h), " ", scalar($r->@*);
say join ",", map {{ $_->() }} @s;
'''


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    rnd = random.Random(seed)
    texts = [program(rnd) for _ in range(count)]
    tally = {}
    with concurrent.futures.ThreadPoolExecutor(int(os.environ.get('JOBS', '2'))) as pool:
        for verdict, text, got, perl in pool.map(run, texts):
            tally[verdict] = tally.get(verdict, 0) + 1
            if verdict in ('WRONG', 'COMPILER', 'HANGS', 'PERL-HANGS'):
                print(f'==== {verdict}\n{text}\n-- language:\n{got}\n-- perl:\n{perl}')
    print(tally)


if __name__ == '__main__':
    main()
