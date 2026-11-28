# Step 19, matching: the independent review

2026-11-28, by a reader who did not write the step (Fable 5.2, a second
agent). The builder had no second agent, so its review was its own
(`patterns.py`, `refusals.ts`, `outputs.txt` here). This one was asked for
a program the compiler takes, that runs without a fault, and prints what
perl 5.42 does not.

**It found four**, and six shapes that perl warns of or dies at and the
compiler took. All ten are refused now (D239), each with a row of
`docs/TRAPS.md` (T560 to T570), rows of `docs/briefs/claims19.py` and
golden tests (5469 to 5497 refusals, 5500 to 5503 `same`). Two of the four
are bugs of perl 5.42's own, which the language has to step round, perl
being the referee.

## The tools

- **`differential.py`**: a generator with a wide grammar. Classes with
  ranges, negation, escapes, `]` `-` `^` at every position and
  POSIX-looking text; `\d \w \s \D \W \S` inside and outside classes;
  every anchor with and without `/m` and `/s`; every quantifier, greedy
  and lazy, on groups and backreferences, with large and zero counts, and
  braces that are no quantifier; alternation with empty branches;
  backreferences to groups closed, open, in another branch and missing;
  `/x` with blanks and comments; every delimiter; about ninety escapes
  and oddities perl has (`\0`, `\10`, `\cA`, `\Q`, `\N{...}`, `(?i)`,
  lookaround, `$a`, `@a`, `$)`); `$` and `@` everywhere. Subjects are
  sampled from the pattern itself, then spoiled (a character dropped,
  added, a newline at the end, the whole doubled), and drawn at random,
  over ASCII and Unicode. Every pattern goes, in a small program, to the
  compiler's whole front end (`classify.ts`: lexer, parser, resolver,
  checker, so the lexer's choice of where a pattern ends is in it) and to
  perl (`classify.pl`). One the compiler takes and perl warns of or dies
  at is a finding at once. The ones both take are run in programs of 150,
  compiled and under perl: for each subject the match where a list is
  wanted (each capture as its characters' numbers, undef told from the
  empty string, `/g` or not), where one value is, and with `!~`. Modes:
  `wide`, `unicode` (the `\d \w \s \b` boundaries), `fold` (`/i`),
  `counts` (T570's family).
- **`pasts.py`**: perl alone. Every taken pattern against every subject
  with no character past U+00FF, kept as bytes and after
  `utf8::upgrade`. A string in the language has no past, so two answers
  there are something the compiler cannot agree with.
- **`counts.py`**: perl against Python's `re` (a matcher with no
  optimiser to go wrong) over T570's family; every pattern they differ
  on is then put to the compiler, and one it takes is a hole.
- **`folds.py`**: `/i` at the edge of ASCII, each pair a program.
- **`review-refusals.py`**: the table the refusal tests are written from,
  by hand.

## WRONG: ran, no fault, printed what perl does not

**W1, T561: `**` after a pattern.** By hand.

    use v5.42;
    for ("a") { say "1" =~ /a/ ** 2; }

perl: `1`. The compiler: `0`. `**` binds tighter than `=~`, so to perl
the right side is `/a/ ** 2`: `$_` matched, the answer raised, and that
number matched as a pattern. The parser had read `("1" =~ /a/) ** 2`.
Outside a loop perl warns (`Use of uninitialized value $_`); inside one
it is silent. Refused: `'**' after the pattern of '=~'`. (`->`, `++` and
`--`, the other operators that bind tighter, were refused already.)

**W2, T567: `\N{U+...}` before a blank in a class under `/x`.** The
generator.

    say " " =~ /[\N{U+41} ]/x ? 1 : 0;      # perl 0, the compiler 1
    say " " =~ /[ \N{U+41}]/x ? 1 : 0;      # 1, both
    say " " =~ /[\x{41} ]/x ? 1 : 0;        # 1, both

After `\N{U+...}` perl skips blanks and a comment under `/x`, in a class
too, where it skips them nowhere else; `/[\N{U+41}#]/x` dies, Unmatched
[. Refused: `\N{U+...}` before a blank or `#` in a class under `/x`.

**W3, T569: a lazy quantifier before a character past U+00FF.** The
generator, once in about 300,000 matches.

    use utf8;
    my @l = "ab" =~ /x??\x{100}|.+/g;
    say "@l";                               # perl: a b    the compiler: ab
    my $t = "ab"; utf8::upgrade($t);
    @l = $t =~ /x??\x{100}|.+/g;
    say "@l";                               # perl: ab

A bug of perl's: a string it keeps as bytes cannot hold U+0100, it gives
up on the lazy `x??` early, and leaves its "lazy" mark set, so the next
quantifier it runs (`.+`) is lazy too. For an equal string kept as UTF-8
it does not. Two answers by the string's past, and a string here has
none. Refused: a pattern with a lazy quantifier and a character past
U+00FF written in it (blunter than the bug, which needs one hard before
the other). After it `pasts.py` finds nothing: 108,918 pairs, as bytes
and upgraded, the same answer each time.

**W4, T570: a count of a string inside a group repeated at least twice.**
The generator, once in about 700,000 matches.

    say "b&aaaa" =~ /b+&(?:a{2}){2}/ ? 1 : 0;     # perl 0, the compiler 1
    say "bxaaaay" =~ /b+x(?:a{2}){2}y/ ? 1 : 0;   # perl 0
    say "b&aaaa" =~ /b+&(?:aa){2}/ ? 1 : 0;       # 1, both

The pattern matches the string, and perl says no: its optimiser works
out a string every match must hold and looks for that first, and here it
works it out wrongly (`perl -Mre=debug`: `floating "b&aa" at 2..`,
`floating "bxaay"`). `counts.py` found 714 such patterns in 20,000 of the
family, 684 of which the compiler took. Refused: a count `{n}` of one
string (characters, one-character classes, groups and counts of them)
inside a group repeated at least twice; all 714 are refused, and
`(?:\d{2}:){2}`, `(?:aa){2}` and `(?:a{2})+`, which perl has right, are
in. A later perl may mend it.

## Taken, where perl warns or dies

| | Program | perl | Now |
|---|---|---|---|
| T560 | `$s !~ /a/ =~ /1/` | warns: Possible precedence problem between ! and pattern match | refused; bracket it |
| T562 | `/\x4-/`, `/[\x4]/` | warns: Non-hex character terminates \x early (the build had refused it before a letter or digit only) | `\x` and one hex digit refused |
| T563 | `/b$#c` newline `/x` | dies: `$#c` is an array's last index; D238 had read an anchor and a comment | `$#` under `/x` refused |
| T564 | `/a{02}/`, `/a{1,03}/` | dies: Invalid quantifier in {,} | a count with a leading zero refused |
| T565 | `/[:alpha:]/`, `/[.a.]/`, `/[=a=]/`, `/[:word]/`, `/[.,ord]/`, `/[.\.]/` | warns: POSIX syntax [: :] belongs inside character classes | see below |
| T566 | `/[^\d\D]*/`, `/[^\S\D]{2}/`, `/[^ \x{0}-\x{10FFFF}\S]{0,0}/` | warns: matches null string many times; Quantifier unexpected on zero-length expression | a negated class that leaves no character refused |

T565's rule is the one to look at. perl guesses at a POSIX class with its
brackets missing by likeness to the names of its classes (`[:alph:]`,
`[xdigit:]`, `[.,ord]` warn; `[:a:]`, `[http:]`, `[aeiou.]` do not). The
refusal is wider than every shape it was seen to warn of
(`posix-classes.pl`: 344,164 classes asked of perl, 2,361 it warns of,
none the rule misses): a class with `:`, `=` or `.` twice (an escaped one
counting with a bare one), or with one of them bare and three letters in
a row. So `[\w.]`, `[a-zA-Z.]`, `[.,:]` are in; `[aeiou.]` is refused
where perl is silent, and is written `[aeiou\.]`.

## What stood

**The match as an expression**, about 190 programs by hand, each the
same as perl, or a refusal, or a fault. Where a list and where one value
is decided: arguments (a failed match is no argument, and the one after
it moves up), `return` and a sub's last statement (by the caller), a
hash's and an array's brackets, `? :`, `||` and `&&`, `push`, `map`,
`grep`, `sort`, `x`, a slice, `join`, `sprintf`. What binds tighter and
looser: `-$s =~`, `$n ** 2 =~`, `$n + 1 =~`, `. =~`, `x =~`, `defined`,
`length`, `uc` and `lc` before a match, `not`, `? :` after one. The left
side a number, a boolean, an element, a chain, a call, an interpolated
string, `$r->$*`; undef and a reference fault. `/g` twice on one string
and after a failed match (nothing leaks: `pos` is cut). A match in a
`foreach`, a closure, a `try`. The slash that divides (`$x / 2 / 3`,
`f() /2/ 1`, `$a[1] /2/ 1`, `$r->@* /1/ 1`, `$x++ /2/ 2`) and the one
that begins a pattern; `m`, `s`, `y`, `tr`, `q` as hash keys and before
`=>`; the four brackets with nesting and escapes; comments under `/x`
with brackets and backslashes in them. Tests 5500 to 5502 keep them.

**The matcher.** On the final tree:

    differential.py, compiled and perl (outputs-differential.txt has each run):
      wide     25000 101   11,463 taken   91,704 pairs   91,696 the same, 1 pattern faults
      wide     25000 102   11,464 taken   91,712 pairs   91,712 the same
      unicode  15000 103   10,619 taken   84,952 pairs   84,944 the same, 1 pattern faults
      fold      8000 104    3,934 taken   31,472 pairs   31,472 the same
      counts    6000 105    2,699 taken   21,592 pairs   21,568 the same, 3 patterns fault
    79,000 patterns drawn, 40,179 taken by the compiler and by perl in
    silence, 38,821 refused; none taken that perl warns of or dies at;
    321,432 pairs run, 321,392 the same, 40 in the five patterns that
    fault (pattern match too long); DIFFERENT: 0.
    pasts.py: 108,918 pairs as bytes and upgraded, perl's answers the same.
    folds.py: 572 pairs under /i: 198 the same, 198 fault, 176 refused.
    counts.py: perl differs from Python's re on 714 of 20,000 patterns;
    the compiler takes none of them.

Before the fixes the same generator ran about 600,000 more pairs, which
is where W2 to W4 came from.

## Notes: not WRONG

- **The step limit is met by plain patterns** (T568, D232). A match
  that fails and begins with a repeat tries every start and every
  length: `/x+y/` faults on 2,260 `x` (2,200 is in), `/\s+$/` on 5,000
  blanks before an `x`, `/\d+\./` on 3,000 digits, `/.*b/` on 3,000
  `a`. perl answers each at once. And the limit does not grow with the
  string: `/(\w+)/g` faults on 4.5 MB of words, `/^a*$/` on four million
  `a`, `/needle/` on twelve million characters. Among random patterns
  over subjects of sixty characters it is rare: five patterns of 40,179 in the last runs. `(a+)+b` on
  28 `a` faults, as meant. Ways out, none taken, Stevan's to choose: try
  a start only where the pattern's first character can stand; a limit
  that grows with the string; some of perl's shortcuts.
- **The machine's stack is not counted against the heap's cap**: it is
  malloc'd, sixteen bytes a frame, so a match can hold some 160 MB
  before the step limit ends it.
- **Refusals a Perl programmer will meet at once**, none new and none
  this step's to change: `if (my ($k, $v) = $s =~ /(\w+)=(\w+)/) { }`
  and `my $n = () = $s =~ /x/g;` (D78: a list assignment is a
  statement), `while ($s =~ /(\w+)/g) { }` (D233), `$1` (D228), a
  variable in a pattern (D229).
- **A message that misstates perl**: under `/x`, `a+ ?` is refused as
  "a quantifier after a quantifier: perl does not compile it". perl
  takes the blank and reads `a+?`. (`a{2} ?` it warns of.) The refusal
  is fine; the reason is not. `m /a/`, a blank after `m`, is refused as
  "the right side of '=~' is a pattern", where perl takes it.
- **Refusals where perl is silent**, counted by `differential.py` (the
  last lines of each run): a backreference inside the group it names
  (about 1,300 of 25,000 random patterns, all of them never matching),
  a quantifier on what can be empty where perl does not warn (`\b?`,
  `^?`), `{n}?` where n is not m. Each is a rule of D226 to D238.
- **`differential.py` loses a batch when perl itself runs past five
  minutes** on one pattern of it (once, seed 22), and does not say which
  pattern.

## The model, and the breakages

`t/models/rematch.py`, the builder's own matcher, drew three patterns
that T570's rule refuses (a `{2}` inside a group repeated twice or
more; perl had those three right, nothing of any length standing before
them). The model leaves the shape out now and was run again: three
lines of 5100, 5102 and 5103 changed, and no expected line.

Each rule of the review was put out or bent, thirty ways
(`docs/briefs/step19-mutations.py`, the breakages named `review:`):
29 of 30 caught the first time. The hole: no test had a count of a string of two characters (`(?:a)` is the character itself to the parser, so the rule's reading of a group was never run); 5497 closes it, and that breakage, run again, is caught. The other 29 were not run a second time.

## What I doubt

- T570's rule and T569's are fences round bugs of perl's that I
  characterised from outside: by `re "debug"` and 714 cases for the
  first, by forty hand cases and `pasts.py` for the second. A sibling
  bug with another shape would not be refused. The generator met each
  about once in half a million matches, so there may be a third it has
  not met.
- T565's rule is a superset by experiment, not by reading regcomp.c.
- perl's optimiser was only compared over subjects of at most sixty
  characters; the step limit keeps long ones from being compared at all.
- The `fold` mode only shows that ASCII folds agree; every character
  past ASCII under `/i` is a fault or a refusal, which `folds.py` holds.
