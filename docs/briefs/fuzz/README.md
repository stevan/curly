# The differential fuzzer

Each step of the language was held to perl by its own model and its own
review, feature by feature (`t/models/`, `docs/briefs/step*-review/`).
This is the first check across the features: whole programs, generated,
compiled, run, and held to perl 5.42.

## How to run it

    python3 docs/briefs/fuzz/run.py FIRST COUNT [--jobs N] [--out DIR] [--stop]
    python3 docs/briefs/fuzz/gen.py SEED            # one program, to read
    python3 docs/briefs/fuzz/reduce.py FILE         # a find, made small
    python3 docs/briefs/fuzz/breakages.py [FIRST [LIMIT]]

`run.py` takes the seeds FIRST to FIRST + COUNT - 1, two workers by
default (the machine is shared), and writes into DIR (`build/fuzz`):
`finds/VERDICT-SEED.pl` for every WRONG, WARNS and CRASH, the program as
it ran with the verdict on its first line, and `totals-FIRST.json`. With
`--stop` it stops at the first WRONG or CRASH. It needs perl 5.42 as
`CURLY_PERL`, Node, and `cc`.

- **`gen.py`** writes a program from a seed: file variables of every
  kind (Int, Num, numeric and other strings, booleans, undef, array and
  hash references, scalar references, closures), named subs with every
  kind of parameter and default and every kind of ending (a value, a
  list, nothing, a `return ... if`), and statements: `say`, `print`,
  `printf`, assignments with every assigning operator to scalars,
  elements, chains and through scalar references, list and slice
  assignments, `++` and `--`, `push` to `splice`, `delete`, `chomp`,
  `chop`, `if`/`elsif`/`else`, `unless`, C-style `for`, `foreach` and
  `for` over every kind of list, `while` and `until`, labels and
  `last`/`next`, bare blocks, statement modifiers (`if`, `unless`,
  `for`, `while`, `until`), `try`/`catch` with `die` of strings and
  references, heredocs, `warn`. Expressions: every operator, the
  builtins, interpolation of every shape the lexer takes, `q qq qw`,
  `map`/`grep`/`sort` (blocks that print, sort blocks that are no
  order), `join`, `reverse`, `sprintf`, `keys`/`values`/`exists`, the
  whole container through a reference, slices, calls through
  references, `__SUB__`. It leans on what has found WRONGs before: a
  name a statement has used already is chosen again more often than
  not (`pick`), so a variable is read and changed in one statement;
  assignments and steps stand inside expressions; fourteen templates
  put known meeting places down whole (an element stored by an index
  that assigns, a closure over a loop's variable and a later store, a
  reference and the array it is to, a sort that counts, numbers at
  2^53 and 2^63). A third of the programs are dense: forty statements,
  no loops, every one reading and changing what the last did. Every
  loop is counted by a variable nothing else touches (T131), nothing
  large is built (T351, D46), a sub calls only the subs before it, a
  closure is assigned once, and a hash's order is never printed (D27).
- **`front.ts`** is the driver's passes in one Node process per worker:
  a program is lexed, parsed, resolved, checked and generated there, and
  `run.py` links the C with one runtime built at the start.
- **`run.py`**: a refusal is counted by its message, and the statement it
  names is taken out (a declaration is kept, with a value nothing
  refuses) and the program asked again, up to 40 times; a fault is
  counted by its message, the statement it names taken out and the
  program run again, up to 12 times. Each run is judged by
  `t/census.py`'s judge, under the knobs of `t/knobs.sh`, perl run plain
  under two hash seeds, with these additions: a fault after the program
  wrote to stderr is LOUD when stdout and stderr are each the start of
  perl's; perl's address of a reference is read as any address, and
  where perl's output moves (an address used as a number) a fault is
  LOUD if what it printed is the start of what both of perl's runs
  print; perl's `Deep recursion` warning is set aside (D67); perl run
  out of memory or not ending is UNJUDGED. perl and the program each
  get 1 GB of memory and 1 MB of output. **WARNS** (perl warns, the
  program is silent) is a finding, as WRONG is.
- **`reduce.py`** takes lines and whole blocks out of a find while its
  verdict stays.
- **`breakages.py`** breaks the compiler and the runtime three ways and
  runs the fuzzer on each until it finds the breakage.

## Broken on purpose

`python3 docs/briefs/fuzz/breakages.py 900000 600`, each breakage put
in, the fuzzer run from seed 900000, the file put back:

| Breakage | Seen after |
|---|---|
| Operand order: the right operand of an arithmetic or comparing operator worked out before the left (codegen.ts, `binary`) | 70 programs |
| A slice off by one: a slice of an array drops its last index (rt.c, `rt_list_add_slice`) | 2 programs |
| A late read made early: a variable copied into a temporary where it is written, not read when its operator runs, D14 (codegen.ts, `var`) | 91 programs |

## What it found

| | What | Done |
|---|---|---|
| T600 | A sub called for nothing that gives back a range: perl makes it a flip-flop, which works out its left end and may stop there, and compares a constant end with `$.` and warns; `(LIST) x N` and `reverse` there work on one value. Found as a WARNS by seed 1001211 (`Use of uninitialized value $. in range (or flip)`) | A fault as the sub begins to give it back (D245; 5701 to 5703) |
| T601 | A sub called for nothing that gives back a sort: perl skips it, its block never run; and a call among what it gives back is for nothing too. Found by hand, looking round T600 | Agreed with (D245; 5700) |
| T602 | An index or key of a chain that changes what holds the container before it (`$v->{f()}` with `f` assigning `$v`, `$a[0][f()]` with `f` assigning `@a`): perl has taken the container and holds no count on it, so it reads undef from a freed one or dies (`Modification of a read-only value attempted`). Found as a WRONG by seed 1002315, reduced by `reduce.py` to 12 lines | Refused (D246; 5720 to 5731, and 5704 for what stays in) |
| T603 | `$v ? (7) x 1 : 0`, and a list repeated by 1 after `&&`, `\|\|` or `//`: perl 5.42 folds the repeat away as it compiles and a jump past it lands on the wrong op, printing garbage or running out of memory. Found as a WRONG by seed 1004968 (perl ran out of memory where the program printed `1.5`), reduced to 6 lines | Refused (D247; 5732 to 5739, and 5705 for what stays in) |

## Totals

Two runs, two workers each, on a machine other agents were loading
(load 12 to 21 on four cores): overnight, seeds 1000000 to 1006899, and
again the next morning on the tree with D245 to D247 in it, seeds
2000000 to 2002299.

| | Programs | Runs judged | SAME | LOUD | UNJUDGED | WRONG | WARNS |
|---|---|---|---|---|---|---|---|
| Overnight, counted (`totals-*.json`) | 5,900 | 40,923 | 4,209 | 36,374 | 334 | 5 | 0 |
| Overnight, seeds 1001000 to about 1001840, from its log (it was stopped before totals were written as it goes) | about 840 | about 6,440 | 584 | 5,826 | 26 | 0 | 4 |
| The morning after | 2,300 | 16,612 | 1,774 | 14,746 | 91 | 0 | 0 |
| **All** | **about 9,040** | **about 63,975** | **6,567** | **56,946** | **451** | **5** | **4** |

A program is one seed; a run is that program compiled, run and held to
perl once, after each repair (about seven a program). Of the 8,200
programs counted, 6,380 were refused as first written (22,743 refusals
in all, under 78 messages, the commonest D77's and D76's) and 1,822
compiled at once; one was given up on. The faults came under 678
messages, the commonest `not a numeric string` (8,915), `undef where a
string is wanted` (8,254) and `undef where a number is wanted` (5,933).
UNJUDGED: perl ran out of its 1 GB (259), wrote past 1 MB (105), did
not end in 15 seconds (60), or printed an address used as a number (1).

**The rate**: the morning's run did 2,300 programs in 62 minutes, 37 a
minute, 4.4 runs a second; overnight 21 a minute. Thirty thousand
programs would have been thirteen hours of it. Nearly all the time is
`cc` over the program's C and the three runs.

**The finds, by class**:

- WRONG, 5: two real, seeds 1002315 (T602) and 1004968 (T603); three
  the judge's own (1003254, 1003333, 1003873), each a program that
  faults where perl carries on for ever or until its memory is gone
  (T131: a `push` onto an array an outer loop is over; `__SUB__` called
  on without end), which the judge took for output perl does not have
  because perl was stopped before it wrote it. The judge now asks first
  whether perl ended (UNJUDGED), and the three are that or LOUD.
- WARNS, 4: three real and one trap, seeds 1001211, 1001791 and 1001838
  (T600); one perl's `Deep recursion` warning (1001301), which D67 sets
  aside and the judge now does.
- UNJUDGED kept to look at, 1 (1000203): an address used as a number,
  where the program had faulted first.
- CRASH (the compiler's own fault, the C not compiling, exit 2), none.
- T601 was found by hand, looking round T600.

The morning's run, an hour on fresh seeds with every fix in, found
nothing, and every file of the overnight run's `finds/` was run again
under the compiler as it is: the two WRONGs are refused (D246, D247),
the three WARNS fault (D245), the rest are as said above.

## What it does not cover

- **Most of what a program does after its first fault or refusal.**
  Only one program in five compiles as written, and about nine runs in
  ten end in a fault; what is held to perl is then only what was
  printed before it. A tenth of the runs, 6,567, ran to their end and
  were compared whole. So the fuzzer finds a program that prints what
  perl does not, and cannot see a fault or a refusal that is stricter
  than it need be at all.
- **Steps 17a on** (classes, fields, methods): this branch was cut
  before them, and `gen.py` writes none.
- **Where perl does not end or runs out of memory**, 451 runs: nothing
  is learned from them. The generator still writes a few (a `push` in
  a loop inside a loop over the same array).
- **Nine thousand programs is few.** Each real find took a thousand
  programs or more to meet; an hour with nothing says the easy ones
  are gone, not that none is left.
- Programs over about 200 lines, and subs that call later subs or
  themselves by name (no call cycle, by construction), so deep
  recursion only through `__SUB__`.
- A hash's order (never printed: D27 makes it the one place a program
  may differ), `each`, and a hash handed to a sub that is not `%opts`.
- Characters past ASCII beyond two literals, `uc`/`lc` of them, and
  `use open`'s layer beyond being there or not.
- stdin, files, the environment, `exit`: not in the language.
- Faults are repaired, not explored: a program that faults has the
  statement taken out, so what follows a fault is tested only in the
  next run.
- The generator knows the types of variables roughly, so about five of
  six runs fault; a fault is checked (what was printed before it must
  be the start of what perl prints), but checks less.
