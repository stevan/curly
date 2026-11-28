# Bends

Step 24's examples (`docs/PLAN.md`, step 24): 54 programs, each written
first as a Perl programmer would write it, then compiled. Where the
compiler refused it, or the program faulted where perl prints on, the
program was bent to the language (D8) and the bend is recorded here:
the Perl, what the compiler said, the decision behind it, what was
written instead, and whether a Perl programmer will resent it. Every
program then prints exactly what perl 5.42 prints, under the test
knobs (a collection at every allocation, poison, a cap of 256 MB), and
its `.expected` is perl's (`t/checks.py oracle`).

This is the first measure of what the language is like to write in,
and it is a floor, not a count: the author had read the language's
Status before writing a line, so the first drafts already left out
`@_`, `local`, `wantarray`, `each`, a bare `$_` in most places, and
`my $x = ... if ...;`, and in five programs wrote round `int` and in
four named a parameter `$a1` before the compiler could say so. Those
are counted below where they are known. A programmer who has not read
the Status will meet more.

What perl does with each construct below is a row of
`docs/briefs/claims24.py` (`python3 docs/briefs/claims.py E24-...`),
run, not remembered: three of the rows were wrong as first written.

## The count

By decision, the bends in the 54 programs: how many programs met each,
and how many places in them.

| What | Decision | Programs | Places | Resented? |
|---|---|---|---|---|
| `@$r`, `%$r`, `$#$r`, `@{$r}[...]` | D108 | 28 | about 89 | mildly: mechanical, and modern Perl writes the arrow anyway |
| `split`, `=~`, `s///` | not yet (steps 19, 20) | 19 | 26 | yes, by everyone: every text program |
| `int`, `abs` | not yet (step 22) | 11, and 5 written round it first | 21 | yes: the commonest builtin a number program wants |
| `scalar @a`, `scalar keys %h`, `scalar(grep ...)` | step 9's rule, no decision | 11 | 17 | yes: it is how `scalar` is written |
| `eval { }` and `$@` | D20 | 5 | 5 | little: `try` is better, and perl's own now |
| `$a`, `$b` as a parameter or a `my` | D55 | 3, and 4 named round it first | 7 | a little: `sub gcd ($a, $b)` is natural |
| `$_` left out: `say for @a`, `map { ucfirst lc }`, `grep { length }` | D85 | 4 | 4 | a little |
| `... or die ...;`, `... or return ...;` | D56, D146 | 3 | 3 | yes: an idiom of every Perl program that opens a file |
| loop variable read-only, `substr(...) =`, `for (1 .. $#a)` changing `@a` | D17, D81 | 3 | 4 | a little; the freeze caught a real in-place sort |
| a `die` over two lines whose message ends in a newline inside `sprintf` or a join | D150 | 2 | 2 | yes, because the message does end in a newline |
| a string as the end of a range: `'a' .. 'z'`, and `1 .. "7"` | D80, T154 | 2 | 2 | the letters, little; the digit string, yes |
| a list assignment as a value: `my $n = () = f();` | D78 | 2 | 2 | little |
| the store makes what the right side read: `$t[$j][$i] = $m->[$i][$j]` | D114, T249 | 1 | 1 | yes: it is the textbook transpose |
| `$cache{$k} //= $f->(...)` with a code reference on the right | D76, D163 | 1 | 1 | yes: it is the textbook memoiser |
| `$;` | D22 | 1 | 1 | no |
| the comma operator: `$buf = $c, return 'number' if ...;` | D15 | 1 | 3 | no |
| `reverse` where one value is wanted | D84 (16d) | 1 | 1 | a little |
| `sort(LIST)` | D89 | 1 | 1 | yes: `sort letters($w)` is a comparator to perl, so the brackets are what is written |
| a format made of literals joined: `"%4s" . "%4d" x 9` | D124 | 1 | 1 | a little |
| an expression as an index in a string: `"$m[$i - 1]"` | D91 | 1 | 1 | a little |
| `do { ... }` as a value | D58 (later) | 1 | 1 | a little |

Of the 54 programs, 11 needed no bend at all: factorial, fibonacci,
even-odd, bottles, ackermann, hanoi, collatz, binomial, sieve, tree and
iterators (numbers, recursion, arrays, closures). Every program that
reads text needed one, nearly all of them `split`.

Two further kinds of bend are the tests', not the language's (at the
end): the oracle check's reading rule for a hash's order made 14
programs sort keys whose order nothing could see, and one program was
cut to a smaller game tree for the test knobs.

## What the language caught

Three times the language stopped a program of the author's that perl
would have run on, and each time the program was wrong:

- **evaluator**: `my $p = $prec{$op};` for an operator the table did
  not have, then `$p + 1`. perl warns `Use of uninitialized value $p`
  and prints a wrong bracketing; the language faults `undef where a
  number is wanted` (D48). Written `$prec{$op} // 4`.
- **roman**: `$v < $next` where `$next` was `$value{$chars[$i + 1]}`
  of a character that is not a Roman digit. perl warns and goes on
  (E24-undef-compare); the language faults (D48). Written `($value{...}
  // 0)`.
- **rational**: an approximation of e as an exact fraction, to 15
  terms. The products pass 2^63, and perl goes on in doubles and prints
  `1.33897666568107e+16/4925819875123623` as a fraction, in silence
  (E24-rational-overflow); the language faults `modulus of a number
  outside the integers` (D35). Cut to 12 terms, where both are exact.

And the freeze (D17) faulted an insertion sort written over `1 ..
$#a` while it moved the elements of `@a`; perl does what was meant
there (E24-insertion), so that one is a bend, above.

## By decision

Each entry: the Perl, what the compiler said, what was written, and a
judgement.

### D108: a dereference without braces

28 programs, about 89 places: `@$cols`, `$#$m`, `%$data`, `@$x[$i ..
$#$x]`, `@{ $grid[$i] }[0 .. 2]`. Refused, `@$ before a name is cut
(D108): an array through a reference is written $r->@* or @{ $r }`;
written `$cols->@*`, `$m->$#*`, `$data->%*`, `$x->@[$i .. $x->$#*]`,
`$grid[$i]->@[0 .. 2]`. perl reads them as the arrow (E24-deref-bare).

Every one is mechanical, and a script did most of them. The cost is
in reading old code, not in writing new: a programmer who writes
modern Perl writes the arrow already (Chalk's own style rule). The
slice through braces, `@{$r}[...]`, is the one a programmer will get
wrong twice: the first rewrite, `$r->@*[...]`, is refused too (`a
subscript after ->@*`), and the right one is `$r->@[...]`.

### Not yet: `split`, regexes (steps 19, 20)

19 programs, 26 places: `split //, $s` (11), `split /,/` and `split
/\./` (5), `split /\n/` (3), `split " "` and `split / +/` (3), and
`=~` with a pattern (7: digits, letters, blanks, an assembler's line).
Refused, `expected a value, found 'split'` or `'=~' is not in the
language yet`. Written as helpers: `chars($s)` (`map { substr($s, $_,
1) } 0 .. length($s) - 1`), `words($s)` (13 lines), `lines($s)` (9,
with `index`), `index` and two `substr` for one comma, and `ge`/`le`
comparisons for a character class (`$c ge "0" && $c le "9"`). The
assembler in stackvm took about 35 lines for the four a regex had.

This is the largest cost in the set, and the one every reader will
feel: no program that reads text is written as a Perl programmer would
write it. A `split` on a literal (`//`, `' '`, `/,/`, `/\n/`) needs no
regex engine and would remove most of it; but perl's `split` always
takes a pattern (`split /./` is every character a separator,
E24-split-dot), so even that is a proposal with a list of what counts
as a literal.

### Not yet: `int` and `abs` (step 22)

11 programs refused (`expected a value, found 'int'`), 21 places, and
in 5 more the author wrote round it before compiling. `int($n / 10)`
became `($n - $n % 10) / 10`, `int(($lo + $hi) / 2)` became `($lo + $hi
- ($lo + $hi) % 2) / 2`, `3 * int($row / 3)` became `$row - $row %
3`, and two programs (numwords, calendar, which is Zeller's congruence
and is nothing but `int`) defined `sub idiv ($n, $d) { ($n - $n % $d) /
$d }`, which is right only for non-negative operands. `abs($c - $col)`
became `$c > $col ? $c - $col : $col - $c`.

`int` and `abs` wait for step 22 with the clock and the random
numbers, and need nothing of either. They are the commonest builtins a
program about numbers wants. One relief found by the way: `" " x 2.5`
and `$a[2.0]` are in, cut toward zero as perl cuts them, so a half
that is only used as a count or an index needs no `int`.

### Step 9's rule: `scalar` takes brackets

11 programs, 17 places: `scalar @solutions` in a `printf`'s list,
`scalar @items` in a closure's return, `scalar keys %count`, `scalar
@{ $d{$_} }`, `identity(scalar @$m)`. Refused, `scalar needs brackets:
scalar(@a)`; written `scalar(@solutions)`. And `scalar(grep { ... }
...)`, refused `scalar names an array, found 'grep'`; written `my
$leaps = grep { ... } ...;`, a count where one value is wanted (D84).

No decision is behind it: step 9's design says "`scalar(@a)`, of an
array and nothing else", and the census lists `scalar` without
brackets among its open refusals. perl's `scalar` is a named unary
operator, as `length` is (E24-scalar: `scalar @a + 1` is the count plus
one, and `scalar @a == 3` compares the count). Of all the refusals met
here this is the one with the least reason and the most bites.

### D20: `eval`

5 programs: `eval { ... }; print "...: $@" if $@;`. Refused at the
`$@` in a string (`'$' in a double-quoted string begins a variable, and
no name is hard against it`), which is the right refusal at the wrong
place. Written `try { ... } catch ($e) { print "...: $e"; }`, which is
better Perl and perl's own since 5.40. Not resented by anyone who has
written `try`.

### D55: `$a` and `$b`

`sub gcd ($a, $b)` (Opal's own gcd, refused), `my $a = [[1, 2, 3],
...]` for two matrices, `for my $b (sort { $a <=> $b } keys %bins)`.
Refused, `$a is not a name a program may declare: $a and $b are the
two values a sort gives its block`. Written `$a1`, `$ma`, `$bin`; and
in bank, bignum and stackvm the author wrote `$a1` before the compiler
could say so. perl takes Opal's gcd in silence (E24-a-param). Resented
a little: `($a, $b)` is the natural pair of parameters, and a program
that sorts nothing gains nothing from the rule.

### D85: `$_` is written

`say for @log;` (two programs), `map { ucfirst lc } words($s)`, `grep
{ length } split / +/, $s`. Refused, `expected a value, found 'for'`
and `lc needs an argument`. Written `say $_ for @log;`, `map { ucfirst
lc $_ }`. perl prints what was meant (E24-say-for, E24-ucfirst-lc).
The message for `say for` does not say what is missing.

### D56, D146: a statement joined by `or`

`my $f = $ops{$op} or die "unknown operator $op\n";`, `my $action =
$turnstile{$state}{$event} or die "...";`, and `my $node =
$list->{head} or return undef;`. Refused, `'or die' after a statement:
a statement is not joined by a word operator here (D56); write die ...
unless ...;` and `return is a statement, not a value`. Written as two
statements, `my $f = $ops{$op}; die "..." unless defined $f;`.

perl's meaning is plain (E24-or-die, E24-or-return): the assignment,
then `die` if it gave something false. D146 kept the door open: "with
files, step 21 may want it". This is the one a Perl programmer will
meet in the first file they open, and resent.

### D17 and D81: places that don't flow

- luhn: `for my $d (reverse split //, $digits) { $d *= 2 if ...; }`:
  the loop variable is read-only (`$d is its loop's variable, and
  read-only`); a `my` copy inside the loop. perl changes the list's own
  element (E24-loop-variable), which here was a temporary.
- luhn, maze: `substr($typo, $pos, 1) = $d;`. Refused, `the left side of
  '=' is a variable, an element, an array, a hash, or a list of them in
  brackets`; written `substr($good, 0, $pos) . $d . substr($good, $pos +
  1)` (E24-lvalue-substr).
- sorting: an insertion sort, `for my $i (1 .. $#a) { ... $a[$j + 1] =
  $a[$j]; ... }`, faults `an array was changed while a foreach is over
  it`: `$#a` names `@a` (D81). Written `my $last = $#a; for my $i (1 ..
  $last)`. perl sorts (E24-insertion). The fault is the language working
  as designed, and the message does not say that `$#a` was the culprit;
  the first reading is "but I'm not looping over `@a`".

### D150: a `die` over two lines

`die sprintf("%s has %d, can't take %d\n", ...)` with its `if` on the
next line, and `die "cycle among: " . join(" ", ...) . "\n"` likewise.
Refused, `a die in a statement, a test or a header over more than one
line: perl names a line of its own choosing there, ...; put it on one
line, or end the message in a newline`. Both messages do end in a
newline, and perl adds no line to either (E24-die-sprintf,
E24-die-concat); the rule looks only for a last argument that is a
string literal ending in one. Written with the condition taken into a
`my` first, so the `die` fits a line. Resented, because the message
the compiler asks for is the message that was written.

### D80, T154: a string as the end of a range

- bases: `my @digits = (0 .. 9, 'a' .. 'z');` faults `a string as the
  end of a range`; written `(0 .. 9, map { chr(ord('a') + $_) } 0 ..
  25)`. String ranges are string increment, which is cut (D52).
- dynprog: `my ($amount, @coins) = @$case;` with `$case = [qw(7 2 4)]`,
  then `for my $x (1 .. $amount)`, faults the same way. perl counts
  `1 .. "7"` as numbers, since both ends look like numbers
  (E24-range-numeric-string, T154). Written with numbers. This one is a
  fault where perl's meaning is the numeric one the language already
  has, met by a value that came from `qw`.

### D78: a list assignment is a statement

`my $count = () = permutations(1 .. $n);` (refused, `an assignment of a
list is a statement`) and `scalar(() = grep { $_ eq "0" } split //,
$f)`. Written `my @all = permutations(...); my $count = @all;`. The
countof idiom is rare and ugly; not resented.

### D114 and T249: the store makes what the right side read

matrix's transpose, `$t[$j][$i] = $m->[$i][$j];`, where `@t` is
returned as `\@t`. Refused, `the store makes what it goes through,
which the right side has already taken: perl takes it after it is
made; take the value into a my first`. Written `my $v =
$m->[$i][$j]; $t[$j][$i] = $v;`.

The rule is sound: with `my @t = (undef)` and `$m = [\@t]`, perl
stores the new row in itself (E24-transpose-alias). But it needs the
element read on the right to exist already and be the very slot made
on the left, which no transpose does, and the compiler cannot see that
`$m` is not `\@t` because `@t` has its reference taken. Resented: this
is the textbook code, and the message is hard to act on without
knowing T249.

### D76 and D163: the memoiser

`return $cache{$key} //= $f->(@args);`, in a memoiser whose `$f` is a
code reference. Refused, `a later part of '//=' can change %cache,
which an earlier part names: perl reads it after the change; take the
value into a my first`: a call through a reference may be any sub with
no name in the program, and one of them is the memoised closure,
which stores into `%cache`. Written as four lines, `return $cache{$key}
if exists $cache{$key}; my $v = $f->(@args); $cache{$key} = $v; return
$v;`. perl prints the same either way here (E24-memo). Resented a
little: it is the idiom, and the refusal is right in general.

### The rest, one each

- **D22**, memoize: `join($;, @args)`, refused at the `$;`; written
  `join(",", @args)` (E24-subsep).
- **D15**, statemachine: `$buf = $c, return 'number' if $k eq
  'digit';`, three times. Refused, `a comma after an assignment's right
  side: perl takes the assignment for the first item of a list; put the
  list in brackets`; written `if ($k eq 'digit') { $buf = $c; return
  'number' }`. perl runs it (E24-comma-return). Clever code, and no
  loss.
- **D84**, strings: `$clean eq reverse $clean`. Refused, `reverse where
  one value is wanted: perl joins its arguments and reverses the
  characters there, which is another function`; written `join("",
  reverse chars($clean))` (E24-reverse-scalar; 16d may bring it).
- **D89**, anagrams: `join "", sort(letters($w))`. Refused, `sort takes
  no brackets of its own`. Without the brackets perl takes `letters`
  for the comparator and sorts the one string it returns
  (E24-sort-name), so the brackets are what a Perl programmer writes.
  Written `sort { $a cmp $b } letters($w)`.
- **D124**, spiral: `printf "%4s" . "%4d" x 9 . "\n", "x", 1 .. 9;`.
  Refused, `printf's format is a string literal with no variable in
  it`; the format has no variable, but is not one literal. Written
  `say sprintf("%4s", "x"), map { sprintf "%4d", $_ } 1 .. 9;`
  (E24-printf-concat).
- **D91**, calendar: `"$month_names[$m - 1] $y"`. Refused, `in a string
  an index is a whole number or a scalar variable (D91): take the index
  into a my first`; written `$month_names[$m - 1] . " $y"`
  (E24-interp-index).
- **D58**, toposort: `return $level{$n} //= do { ...; $max + 1 };`.
  Refused, `expected a value, found 'do'`; written out as a test, the
  work and a store (E24-do-block).

## The tests' own bends

- **The oracle's reading rule** (`t/checks.py`, `hash_order_shown`)
  rejects a test where a hash's order could show, by pattern, and errs
  toward rejecting. 14 programs met it where no order could show:
  summing `values %h`, building one hash from `keys` of another,
  `keys %h` handed to a function that makes a set, a hash's truth
  (`unless %$data`), a hash handed to a sub through a code reference,
  and **`my (%start, %end);`**, a declaration of two hashes in one
  `my`, read as "a whole hash without sort". Each was given a `sort`
  it does not need, or split into one `my` per hash. The declaration
  is a false alarm of the rule that a fixture could pin; the rest are
  the price of reading by pattern, and were cheap.
- **The knobs**: tictactoe's first draft played from an empty board,
  549,946 positions; under poison (a collected string's memory is never
  used again, and the cap counts it) it ran out of its 256 MB, and
  without the knobs took four seconds. The game now starts two moves
  in. Not a difference from perl, but a measure: a program the size of
  a small game tree is too big for a golden test as the tests run.

## Five refusals to loosen

In order of how much they would give back, each with what perl does.

1. **`scalar` without brackets** (step 9's rule; 11 programs). perl's
   `scalar` is a named unary operator: `scalar @a`, `scalar keys %h`,
   `scalar @a + 1` (the count plus one), `scalar @a == 3`, and
   `scalar(grep { ... } @a)` are each what they look like
   (E24-scalar). Take it in with `length`'s rules (D41) and `keys`'s
   (T220), and `scalar` of a `grep` or `map` as its count (D84).
2. **`EXPR or die LIST;`, `EXPR or return ...;`, `or next`, `or last`**
   (D56, D146; 3 programs here, and every program that opens a file).
   perl assigns, then dies if the value was false (E24-or-die,
   E24-or-return). A statement that is an assignment or a call, then
   `or` and one of those four, is a second spelling of `unless` and
   changes no meaning the language has.
3. **`sort(LIST)` with the bracket hard against `sort`** (D89; met once
   here, and `sort(keys %h)` is in the Status's list of what a Perl
   programmer writes). perl is silent for it (E24-sort-brackets) and
   warns only with a blank between (`sort (...) interpreted as
   function`, E24-sort-blank, T190), which can stay refused.
4. **A message that ends in a newline inside `sprintf` or at the end of
   a join** (D150; 2 programs). perl adds no line when the string it
   is handed ends in a newline (E24-die-sprintf, E24-die-concat): the
   compiler can see it when the last piece of a concatenation is a
   literal ending in one, or a `sprintf`'s literal format ends in one.
5. **The store that makes what the right side read** (D114, T249; the
   transpose). perl makes the hop after it has taken the right side,
   which differs only when the element read on the right exists and is
   the slot the hop makes (E24-transpose-alias; when it does not exist
   perl stores undef, as the language would, E24-transpose). A check
   as the store runs, faulting in that one case, would take the
   textbook code in, in exchange for a runtime test the refusal does
   not need.

And two that are not refusals by decision, but the largest costs in
the set, to pull forward from their steps if they can come alone:
**`int` and `abs`** from step 22 (16 programs; they need nothing of
the clock), and **`split` on a literal** from step 20 (19 programs met
`split` or a regex; perl's `split` always takes a pattern, so the
literal forms would need a list, E24-split, E24-split-dot). Next after
those: a numeric string as the end of a range (T154: perl counts `1 ..
"7"` as numbers), and `$a`/`$b` as parameters of a sub that sorts
nothing.

## Not on this machine

The table's "about 25 small programs" of Crayon's plan (`stevan/p5-Crayon`,
`docs/superpowers/plans/2026-03-31-crayon-interpreter.md`) could not be
read: the repository is not on this machine, and attaching it was
refused. They are described as subs, classes, references and `try`;
the programs here cover the subs, references and `try` of that
description with programs of their own (closures-stack, bank,
linkedlist, tree, pqueue, events, inventory), and the classes wait for
step 17. Opal's (`stevan/pp`) were read: factorial, fibonacci, gcd,
even-odd and bottles are its `tests/`, ported and grown; ackermann,
hanoi, collatz, binomial and sum-digits its `author/TESTING.md`.
