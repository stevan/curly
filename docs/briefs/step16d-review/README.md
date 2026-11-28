# The reviews of step 16d and of what the census's reading asked for

Two reviews stand here.

**The builder's own** (2026-11-27): `part1.py`, `part2.py` and `part3.py`,
generators held to perl, run as a separate pass because no second agent
could be spawned in the builder's session. `docs/PLAN.md`, "What the
census's reading asked for, 16d and the lone range, as built", has what
they found (T663, T664, T672) and their counts. No WRONG.

**The independent review** (2026-11-28): a second reader, who did not
write the step, given the proposal, the decisions D250 to D262, the
tree at c9c2fd8 and perl 5.42, and asked for a program the compiler
takes, that runs without a fault, and prints what perl does not. Its
driver and every case it ran are in `reader/`. The rest of this file is
its account.

## The independent review

### How it was done

`reader/drive.py` takes case files (a Python module with `cases()`,
which yields a name and a program), writes each program to a file,
compiles it, runs it under the tests' knobs (a collection at every
allocation, poison, the cap), runs perl on the same path, and gives a
verdict: REFUSED, NOTPERL (perl does not compile it and the compiler
refuses it), SAME (stdout, stderr and exit status are perl's), LOUD (a
fault, after a prefix of what perl prints), WRONG (anything else: a
different answer, a warning of perl's the program did not fault for, or
a program the compiler takes and perl does not compile), HANG (looked at
by hand; each one was perl or both running for ever, T131's kind, and
the program at fault was the reviewer's). perl's output is bounded (a
megabyte) and timed.

    python3 docs/briefs/step16d-review/reader/drive.py docs/briefs/step16d-review/reader/*.py

The case files, by what they push on:

| File | Programs | What |
|---|---|---|
| `hand_range.py` | 127 | D259 by hand: ends that are expressions, calls, `$#a`, `$#{$r}`, counts, strings, floats, undef; the block changing what the ends name; closures; `map`, `grep`, `sort`; the modifier; brackets, a comma, `reverse` |
| `hand_out.py` | 320 | Every way out (`next`, `last`, labels, `return`, `die`, `or next`) of a lone range's loop inside and outside loops that froze, and the containers changed after |
| `gen_mix.py` | 900 | Random programs: loops over ranges whose ends name arrays, hashes, scalars, references and subs, blocks that change them by name, through references, in subs and in closures made in the loop, `$#a = N`, `undef`, `do { } while` inside |
| `hand_or.py` | 176 | D260 by hand: precedence, `my`, list assignments, a sub's last statement, `map` blocks, labels, lines |
| `gen_or.py` | 2,073 | 102 left sides by `or` and `and` by 13 statements after the word, at the top, in a sub, and as a sub's last statement in list and scalar context |
| `hand_do.py` | 231 | D253, D251, D252 by hand |
| `hand_misc.py` | 164 | D250, D258, D262 by hand |
| `gen_scalar.py` | 1,879 | 17 operands of `scalar` by 53 things that may follow; 113 `sort(...)` in three places; eight by 15 things after the bracket |
| `hand_str.py` | 298 | D254 to D257 and D261 by hand: `substr` of four, `__LINE__`, POD, `__END__`, the case escapes, the special cases of Unicode, a `die` over lines |
| `gen_die.py` | 952 | D261: 133 last arguments of a `die` or `warn` by 18 places over more than one line |
| `gen_pod.py` | 553 | POD, `__END__` and `__DATA__` at every line's start of seven programs written a token to a line; 22 lines that might begin POD and 19 that might end it |
| `gen_case.py` | 260 | `uc`, `lc`, `ucfirst`, `lcfirst`, `quotemeta` and the case escapes over strings dense with U+0345, marks, sigmas and the letters that map to several (12 strings a program) |
| `gen_esc.py` | 1,775 | Random strings of case escapes, text, variables and other escapes in double quotes, `qq` and heredocs; `substr` of four over every offset and length from -7 to 7 on five strings |
| `hand_more.py` | 164 | After the first findings: scopes of a `my` before `or die`, lines, POD in every kind of block, `__LINE__` and `__FILE__` as operands |

### What it found

Five ways to be WRONG, T673 to T677 in `docs/TRAPS.md`, each a row of
`briefs/claims16d.py`, each fixed and held by golden tests 6260 to 6273
(written from `reader/tests.py`, a table by hand).

**T675, WRONG (prints what perl does not). `uc` of a U+0345 before a
combining mark.** D257's check that a string is mapped a character at a
time had one exception, two U+0345 together (T664). The rule perl has
is wider: `uc` holds the capital iota a U+0345 makes back until the
next character that is no mark, so the iota moves past every mark
after it, and two with only marks between make one.

    use v5.42; use utf8; use open ':std', ':encoding(UTF-8)';
    say uc "\x{345}\x{300}";
    --- perl
    ̀Ι           (U+0300 U+0399)
    --- the compiler, before
    Ὶ           (U+0399 U+0300)

    say uc "a\x{345}\x{300}";      perl: A U+0300 U+0399; before: A U+0399 U+0300
    say uc "\x{345}\x{301}\x{345}"; perl: U+0301 U+0399;  before: U+0399 U+0301 U+0399

46 of `gen_case.py`'s 260 programs differed. The characters perl moves
it past are exactly its `\p{M}`, 2,501 of them (claim `T675-marks`).
**Done**: a fault, `uc of U+0345 before a combining mark: perl moves it
past the mark`, D257's own choice for the one case it knew, widened; the
marks are asked of perl by `briefs/step16d-cases.py` and kept in
`runtime/cases16d.c` (`case_mark`, 321 ranges), and the generator's own
check of "a character at a time" now has a mark after a letter and a
U+0345 before a letter in its pool. Tests 6266 to 6268. The amendment
note under D257 says that perl's rule could be ported instead, now that
the table is there.

**T677, WRONG. A `\u` or `\l` first in a run.** D256 had "first in a run
they apply over it (`\L\u` is `\u\L` to perl)". perl swaps exactly two
pairs, `\L\u` and `\U\l`; any other (`\U\u`, `\L\l`, `\Q\u`, `\Q\l`)
is inside the run and ends at its `\E`. The compiler put every one
outside, over the rest of the string:

    my $e = ""; say "\U\u$e\Eabc";
    --- perl
    abc
    --- the compiler, before
    Abc

and `"\L\l$e\EABC"` was `aBC` for perl's `ABC`. With nothing between
the `\u` and the `\E`, perl's answer is one no rule gives (`"\U\u\Eabc"`
is `ABC`, `"\Q\u\Ea.c"` is `a\.c`). **Done**: agreed with perl (the two
swapped pairs go on past `\E`, the others end with the run), and `\E`
hard after a `\u` or `\l` in a run is refused, as is a second `\u` or
`\l` first in a run. Tests 6271 to 6273; D256's amendment note.

**T676, WRONG (perl warns; and a different answer). `$#a = N or die`.**
D251 made `$#a = N` a statement alone, and D260's `or die` took it on
its left all the same:

    my @a = (1, 2);
    $#a = 0 or die "e\n";
    --- perl
    Found = in conditional, should be == at x.pl line 3.
    e
    --- the compiler, before
    e

and with `$#a = -1 and die "e\n";` perl dies (-1 is true) where the
compiler went on. 15 of `gen_or.py`'s programs. **Done**: refused,
`'or die' after $#a = N: setting an array's last index is a statement
alone (D251)`. Tests 6269 and 6270.

**T674, WRONG (takes what perl does not compile). POD where no statement
may begin, to perl.** The lexer took "after a block's closing brace" and
"after a `;`" for places a statement may begin. Not so after the block
of a `do`, a `map`, a `grep` or a `sort`, nor after a `;` between a
`for`'s brackets:

    my $i = 0;
    do { $i++ }
    =pod
    =cut
    until ($i);
    say $i;
    --- perl
    Can't modify constant item in scalar assignment at x.pl line 6, near "cut
    until"
    --- the compiler, before
    1

**Done**: refused there (the lexer marks such a block's closing brace,
and looks for an open round bracket before a `;`); `__END__` and
`__DATA__` go by the same rule. POD inside those blocks, and between an
`if`'s block and its `else`, stays in, as perl has it. Tests 6261 to
6265.

**T673, WRONG (takes what perl does not compile). `=_x` begins no POD.**
perl's POD begins with `=` and a letter; the lexer took a word's start,
`_` among them. **Done**: a letter of ASCII. Test 6260.

### What stood

- **D259, the lone range.** 1,347 programs written to break it, by hand
  and at random: no difference. The ends are worked out once in every
  shape tried, a string as an end faults (`a string as the end of a
  range`), the freeze of an enclosing loop is given back once on every
  way out, a closure over the variable has its own number, and `map`,
  `grep` and `sort` over a range still freeze.
- **D260, `or die`**, but for T676: 2,249 programs. Every left side perl
  warns of, or reads in list context, or takes its `or` into, is refused
  already (D53, T106, T109, T139, T670) or faults (D18).
- **D261**: 952 programs, 361 SAME and 591 refused, none differing. The
  judge says "ends in a newline" only where it must.
- **D250, D258, D262**: 2,043 programs, none differing.
- **D253, D251, D252**: 231 by hand and what `gen_mix.py` made.
- **D254, D255's `__LINE__` and `__FILE__`, `quotemeta`**: none
  differing.

### Notes (nothing WRONG)

- NOTE, a document misstating the language: `docs/LANGUAGE.md` still
  said of the case escapes "Not yet" in one place and listed them among
  the refused escapes in another. Mended.
- NOTE, stricter than needed: `for my $i ((0 .. $#a))` and `for my $i (0
  .. $#a,)` are lone ranges too by the compiler's reading (they ran as
  perl runs them); a string range, `'a' .. 'e'`, is a fault everywhere,
  which is step 9's and not this step's.
- NOTE: a fault in the test of a `do { } while` names the line of the
  `do`; perl names the line of the block's last statement (as it does
  for a `while`'s test, T317). Both are faults here, so nothing shows.
- NOTE, stricter than needed: a `\u` or `\l` after a run's start stays
  refused though perl's rule for it is now known (it is in the run).

### What the reviewer doubts

- The fault for U+0345 before a mark keeps D257's choice; perl's rule is
  three lines and the table is there. Stevan's.
- `gen_mix.py`'s programs are refused or fault a third of the time; the
  603 that ran to the end are the evidence for D259, with the 447 by
  hand.
- perl's rules for the case escapes were read from its answers, not its
  source: `gen_esc.py` holds the subset the compiler takes to perl over
  1,400 random strings, and a shape it never made could still differ.
- Nothing here tried a second machine: the Mac's libc is not in it.
