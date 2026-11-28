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

(Filled in at the end of the run.)

## What it does not cover

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
