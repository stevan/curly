# The census's open refusals, read (2026-11-27)

Before this reading the census (`t/census/census.json` at 41a9025) had
1,300 SAME, 178 LOUD and 1,251 REFUSED, **822 of them "open"**: refused
with no step and no decision named, and read by nobody. Every one is read
here, by the compiler's message and the text at the place it names.
`classify.py` beside this file does the reading and prints it (the
section below is its output, cut down); it has no cause left over.

What came of it:

- **763 of the 822 were decided already, or wait for a step that is
  planned.** 630 are refused by a decision (`a`), and moved to
  `t/census/by-design/` by `t/census.py --sort`, each with its decision
  in `BY-DESIGN.tsv`; 133 wait for a step (`b`). The census's reason
  table (`REASONS` in `t/census.py`) has a row for each, under "the open
  refusals, read". A message the compiler gives for more than one thing
  (`after '$' comes a name` is `$@`, `$,`, `$1` and `$::x`) is told
  apart by the text at the place: a row may now ask the line before the
  place and from it on.
- **59 are truly open**, five causes, every one of them a construct the
  language could take in: they are the ranked list below (`c`), and one
  that needs Stevan (`d`).
- **The census after the reading, before the new corpus** (the last
  section has both): 1,300 SAME, 178 LOUD, 621 REFUSED (562 for a later
  step, **59 open**), 4 UNJUDGED, of 2,103 run; 3,477 by design; no
  WRONG; no probe left SAME.
- **The 178 LOUD**: every fault is one a decision intends. None is
  unintended (the last section).

## The ranked list: what to take in (c), by probes freed for the work

"Frees" is measured, not guessed, but it is an estimate: each probe of
the cause was rewritten by hand-made regexes into what the language
takes today with the same meaning (`scalar @a` to `scalar(@a)`,
`undef $x;` to `$x = undef;`, `$#a = 0` to `splice(@a, 1)`, `do { B }
while (C);` to `while (true) { B; last unless (C); }`, `do { B }` to
`sub { B }->()`), compiled, run, and held to perl's run of the
original. What then prints what perl prints is counted as freed; what
is refused behind it, or faults, is not. Every rewrite was run; none
printed what perl does not.

1. **`scalar` without brackets: `scalar @a`, `scalar @{ $r }`,
   `scalar %h`.** 10 probes, **10 freed** (and an 11th, `pp-c332`,
   with `undef @a` below). A parser tweak: `scalar` read as the named
   unary operator it is, over what `scalar(...)` takes now. perl, run:
   `scalar @a + 1` is `scalar(@a + 1)` (named unary binds looser than
   `+ - .`), 4 for three elements either way; `scalar @a . "x"` is
   `3x`; `scalar @a x 2` is `33`; `scalar @a < 4` is `1`; `(scalar @a,
   9)` is `3 9`; `scalar keys %h` and `scalar %h` the count. The
   operand of `+ - . x` is in scalar context whichever way it is read,
   so no reading differs; refuse `scalar` before anything but an array,
   a hash or a whole container through a reference, as now. `scalar
   reverse ...` stays 16d's.
2. **`$#a = N;`.** 8 probes, **8 freed** (6 through `splice`, the 2 that
   grow the array by hand: `defined $b[2]` is `u` as perl prints). D80
   left it "until its step" and no step has it. Small to medium: a
   statement on a named array (and then `$#{ $r } = N` and `$r->$#* =
   N`, now cut beside it), the runtime's array made that long, a change
   to the array for D76, D77 and the freeze, as `splice` is. perl, run:
   `$#a = 1` cuts to two; `$#a = 3` grows with elements that are undef
   and not `exists`; `$#a = 1.7` is two elements; `$#a = "2"` three;
   `$#a = -1` empties; **`$#a = -2` and `-5` empty in silence**, and an
   undef warns. Recommend: a whole number from -1 up, a fault below -1
   and for undef (D48), a Num cut as an index is. The array's holes stay
   invisible only while `exists` of an element stays out (the (d) item).
3. **`do { ... } while COND;` and `until`.** 11 probes, **8 freed**
   (`ps06` then refused for a loop variable changed, D17; `lw53` for
   `$_` changed; `loops-05` for `%ENV`). D58 left it "for the step that
   takes `do BLOCK`". Medium: a loop kind of its own that runs the block
   first, a C `for (;;)` with the test at its end. **It is no loop to
   perl** (T64): run, `for my $k (1..3) { do { $i++; last if $i == 2 }
   while ($i < 5); print "k$k\n" }` leaves the `for`, and prints nothing
   of `k1`. So a `last` or `next` with no label inside one is refused,
   as D59 refuses it in a bare block; with a label it leaves its loop, as
   perl has it.
4. **`undef $x;`, `undef @a;`, `undef %h;` as statements.** 8 probes,
   **5 freed**, a sixth with `scalar` above (`yf48` and `ps21` then
   refused: `undef` of a loop's variable changes the list's element, to
   perl, D17). A parser tweak, read as `$x = undef;`, `@a = ();`, `%h =
   ();`, so every walk sees an assignment. perl, run: `undef @a` leaves
   `scalar(@a)` 0, `undef %h` leaves 0 keys, `my $r = undef $x` makes
   both undef. Recommend the statement alone (as `chomp`, D130), not a
   value; `undef $a[0]` and `undef $h{k}` with it, as the assignment of
   an element.
5. **`do { ... }` as a value.** 14 probes, **5 freed** (`s10`, `a33`,
   `yc78`, `yf92`, `f21`); behind it D76 refuses 3 (`($x, do { $x = 7
   })` reads `$x` after the change, to perl: `7 7`), a builtin's `$_`
   2, a useless constant 2 (`do { 1; 2 }`: perl is silent for 1, the
   language refuses it), `%ENV` 1, `require` 1. **Machinery**: a block
   that is a value, statements in the middle of an expression, a scope
   of its own, generated where it stands as a `map` block is, and seen
   by every walk as code that runs there. Its value is its last
   statement's: perl, run, gives the condition's value for `do { if
   ($x > 2) { "a" } }` when the test fails (an empty string), and
   `do { (4, 5, 6) }` where one value is wanted warns, so its last
   statement must be an expression, by D18's rules for a sub's.

Not in the list because they are decided, though they hold the most
probes (Stevan's levers, if he wants them):

- **`my $x = shift;` in a sub with no signature: 355 probes** (D17,
  D105). Rewritten to a signature, `sub f($x, @) { ... }`, **289 of the
  354 bare `shift`s print what perl prints**; 20 more then want
  `@ARGV`, 14 a `$a` or `$b` declared. A signature is not the same
  thing (perl's missing argument is undef, the signature's a fault), so
  this would be a reading of `shift` at the head of a body, not a
  rewrite.
- An assignment to what is not a variable (D56, D17): 87 probes, almost
  all perl5-son's order-hunters, `($x = 5) += 2`, `($c ? $p : $q) = 7`.
- `$@` (D20): 63, every one with a block `eval`.
- `%ENV`, `@ARGV`: 50, step 21's.

## Needs Stevan (d)

- **`exists $a[I]`, `delete $a[I]`.** 8 probes. D80 left them "until
  their step", and no step has them. **perl's arrays have holes**, run:
  `my @a; $a[5] = 1;` then `exists $a[2]` is false and `exists $a[5]`
  true, `scalar(@a)` 6; `delete $b[2]` of the last element shrinks the
  array, of the first leaves a hole. The runtime has no holes: an
  element is a value or undef. Options: (1) keep them out (the
  recommendation; nothing a program prints needs them that `defined`
  does not give); (2) holes in the runtime, a bit an element carries,
  made by a store past the end and by `$#a = N`, which is machinery and
  touches every array; (3) `exists` as `I < scalar(@a)`, which is WRONG
  after `$a[5] = 1`, so not an option.

## Every cause

Verdicts: `a` decided (the decision named), `b` waits for the step
named, `c` the ranked list, `d` Stevan's. Counts are of the 822; three
examples each, the probe, its place and its line.

| cause | verdict | probes | what |
|---|---|---|---|
| bare-shift | a D17 | 355 | `shift`, `pop` with no array |
| lvalue-expr | a D56 | 87 | an assignment to what is not a variable |
| eval-error | a D20 | 63 | `$@` |
| env-argv | b 21 | 50 | `$ENV{X}`, `@ARGV` |
| open | b 21 | 22 | in-memory files |
| punct-global | a D22 | 21 | `$,`, `$"`, `$/`, `$\` |
| do-block | c | 14 | `do { }` as a value |
| bitwise | b 22 | 14 | `| & ^ ~ << >>` and their assignments |
| implicit-it | a D85 | 12 | a builtin with no argument, `$_` |
| regex | b 19 | 12 | `s/^\s+//`, `qr`, `split /,|;/`, `!~` |
| do-while | c | 11 | `do { } while` |
| step-expr | a D56 | 11 | `++` on what is not a variable |
| package-var | a D19 | 10 | `$::x`, `$main::v`, `%::h` |
| scalar-bare | c | 10 | `scalar @a` |
| last-index-store | c (D80) | 8 | `$#a = N` |
| undef-var | c | 8 | `undef $x;` |
| array-exists | d (D80) | 8 | `exists $a[I]`, `delete $a[I]` |
| process-var | b 21 | 7 | `$|`, `$0`, `$$`, `$^O`, `$^X` |
| array-target | a D80 | 6 | `(@a, @b) = ...`; a comma after an assignment |
| list-assign-value | a D78 | 6 | `scalar(($x, $y) = ...)` |
| substr4 | b 16d | 6 | `substr` of four arguments |
| map-brackets | a D87 | 5 | `map(...)`, `grep(...)` |
| sort-word | a D87 | 5 | `sort by_num LIST`, `sort $by LIST` |
| kv-slice | a D104 | 5 | `%h{...}`, `%a[...]` |
| scalar-reverse | b 16d | 5 | `scalar reverse` |
| minus-letter | a D21 | 4 | `-e`, `n()-n()`, `tr/a-c//` (T135) |
| no-warnings | a D16 | 4 | `no warnings;` |
| prototype, slice-target, map-block, phase-block, typeglob | a D21, D100, D85, D20, D4 | 3 each | |
| pod, numeric-fn, match-var, processes | b 16d, 22, 19, library | 3 each | |
| lock-select, sub-attribute, label, word-op-statement | a D22, D165, D61, D56 | 2 each | |
| bytes, glob | b bytes, 21 | 2 each | |
| splice-brackets, format, one-key-slice, pod-data, print-brackets, vstring, printf-value, undef-range, my-modifier, reversed-op, at-underscore, return-list, sub-in-block | a D80, D22, D104, D20, D21, D38, D21, D15, D56, D56, D17, D18, D72 | 1 each | |
| state | b D160 | 1 | `state` |

`python3 docs/briefs/census-open/classify.py /tmp/before.json` (the
file at 41a9025, as its docstring says) prints the three examples of
each; `--list CAUSE` every probe of one.

Three causes are not one decision's alone, and the row names the one
nearest: `lvalue-expr` holds `substr(...) = ...` (SURFACE.md cuts it,
with no decision: D17's "places don't flow" is the reason); `typeglob`
is D4's subset, which has no typeglobs; `punct-global` and
`lock-select` are D22's list. SURFACE.md says two things of two rows
the reading met: `$#a = N` is "Cut" in Data and "Later" two rows on, and
`%h{...}` is "Cut" in Operators and "Later" in Data; D80 and D104 say
"until its step" and "not proposed".

## The LOUD probes (178)

Every fault is a documented one; **none is unintended**.

| fault | probes | decision |
|---|---|---|
| an array was changed while a foreach is over it | 85 | D17, D80 (the freeze; `$#a` in a range names the array) |
| undef where a reference is wanted | 32 | D107 |
| not a numeric string | 12 | D40, and D52 (`"abc"++`, perl's string increment) |
| integer overflow | 12 | D23 |
| a slice past the end of the array, where perl would make the elements | 5 | T161, D80 |
| f returned a list where one value is wanted | 5 | D18 |
| a string as the end of a range | 4 | T154, D80 |
| a key that is not there in a foreach | 4 | T216 |
| a hash was changed while a foreach is over it | 3 | D17 (12b) |
| a whole float this size prints two ways | 3 | D36 |
| an element past the end of the array in a foreach | 2 | T161 |
| a slice with a key that is not there | 2 | T216 |
| not a number | 2 | D37 |
| substr outside of string, float overflow, negative repeat count, undef where a number is wanted, missing argument in sprintf, a negative zero to %e, f has no value | 1 each | D13, D37, D44, D48, D126, T282, D18 |

The freeze's 85 are the blunt one: many are `for my $i (0 .. $#a) {
$a[$i] = ... }`, which perl runs well, and the language faults because
`$#a` names the array (9b, "the loop that changes an array as it goes
takes the count into a `my` first"). Intended, and the largest group of
faults a Perl programmer will meet.

## The new corpus (`t/census/import_more.py`)

Read from: perl 5.42.0's `pod/*.pod` (the tarball, sha256 e093ef18...;
every verbatim block, and every run of them, but the perl5*delta
histories), pvm's other `.pl` files (its parser's test data, outside
`conformance/mdtest`, which import.py has), PerlOnJava's unit tests as
pvm carries them (a `.t` with no Test:: module as it is; one using only
`ok`, `is`, `isnt`, `pass`, `fail`, `plan`, `done_testing`, rewritten
statement by statement to `say` of what it tests), and perl5-son's and
Chalk's `.pl` files outside the trees import.py reads (same revisions as
import.py's). A program is kept only when it is a probe: with `use
v5.42;` in front, perl runs it plain, stdin empty, exit 0, nothing on
stderr, something on stdout, the same under the census's eight seeds;
and its text touches no file, environment, clock, process or network,
loads no module but a pragma, and is 200 lines at most. A pod's example
whose only complaint under strict is undeclared globals gets a `my` of
each (the pods are written without strict); nothing else in a pod is
changed. The rest is dropped, not put in `not-perl/`: these sources are
not probes, and most of what they hold is not a program.

8,589 programs read, 689 distinct and allowed, **304 probes imported**:
pod 162, pvm-more 70, perlonjava 45, son-more 21, chalk-more 6. Their
verdicts, apart from the old corpus's:

| source | SAME | LOUD | REFUSED later | REFUSED open | by design |
|---|---|---|---|---|---|
| pod | 52 | 1 | 61 | 3 | 45 |
| pvm-more | 1 | 0 | 3 | 0 | 66 |
| perlonjava | 0 | 1 | 23 | 3 | 18 |
| son-more | 5 | 1 | 6 | 0 | 9 |
| chalk-more | 5 | 0 | 0 | 0 | 1 |
| **all** | **63** | **3** | **93** | **6** | **139** |

**No WRONG.** The 3 LOUD are documented faults (`"inf"` read as a number,
D40; a character past ASCII printed with no `use open`, D39; a list
returned where one value is wanted, D18). Of the 93 waiting, 63 are
regexes (step 19), 13 `pack` and friends, the rest 21, 17, 16d, 22. By
design: `qw` with a backslash or comma (D121) 39, a pragma (D16) 31, D17
15, and a tail. The 6 open: `$#values = 7` (the ranked list's item 2),
`vec` twice and `pos` (SURFACE.md cuts both, with no decision), a
flip-flop `...` (cut, no decision), `foreach my ($k, $v)` (Later, not
proposed). New rows of the reason table cover what the new corpus
brought that a decision already says (D121, D123, D19, D85, D92, D15,
D38, and `$?`, `$^V`, `$^N`, `\N{...}`, `blessed` by their steps).

The census with both: **1,363 SAME, 181 LOUD, 720 REFUSED (655 later,
65 open), 4 UNJUDGED, of 2,268 run; 3,616 by design; 206 that perl stops
at; no WRONG.** The old corpus alone is as above (1,300, 178, 621 with
59 open, 4).

The pods gave less than hoped: perldsc and perllol gave nothing, their
examples printing their output inside the same verbatim block, or using
globals with `local`, or reading files. A Test::More rewrite beyond
these words was not tried: the files that use more are about modules,
threads and `B::Deparse`, and would be refused whole.

The corpus's licence is to be settled with the repository's, as
`runtime/sort.c`'s is (D82): the pods are under perl's terms, PerlOnJava
under its own (perl's terms), and SOURCES.tsv says so.
