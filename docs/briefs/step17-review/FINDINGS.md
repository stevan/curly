> **How this file came to be here.** The reviewer's harness refused it a
> write to the repository, so it returned this text and left its programs
> on disk; the proposer saved the text as it came, below this note. Every
> program beside it (`NN-name.pl`, with `NN-name.out`) was rerun under
> perl 5.42.0 (and the `12-*` ones under the roles perl) before this file
> was committed: all 80 printed what their `.out` says. Each is a row of
> `briefs/claims17.py` (`R17-NN-name`), and the findings are T422 to T437
> in `TRAPS.md`, answered in `PLAN.md`, step 17, "What the review found".

# Step 17a, adversarial review: findings

I am a reviewer who did not write the proposal (2026-11-27).

**What I read:** `CLAUDE.md`; `docs/PLAN.md` from "### 17. Classes" to "### 18. Modules"; D160 to D166, D170 to D177, D16 to D19, D69, D76, D77, D109 and D112; T400 to T421; and `briefs/claims17.py`.

**What I ran:** step 17 is not built, so I reasoned from the proposal's text. I ran the existing compiler only to see how built parts behave today. Every statement about perl comes from a program run under `/opt/perl-5.42/bin/perl` (5.42.0), and the 17b ones under `/opt/perl-5.42-roles/bin/perl`; outputs are pasted.

**How the programs are written:** each begins with `use v5.42;` and `use experimental 'class';`, left out below, so code starts at line 3. The programs are kept beside this file as `NN-name.pl` with `.out` (stdout, stderr, `exit: N`). The number in a file's name is its finding's number.

**How the findings are arranged:**
- 1 to 8 are WRONGs.
- 9 to 11 are places where the text is ambiguous, and the obvious build is WRONG.
- 12 is about 17b.
- 13 to 17 are lesser points and holes in the test plan.

## 1. WRONG: inside a class, `helper()` means `P::helper`, not the program's sub

`class P {}` is `package P`. perl looks a call's name up in the current package and never falls back to `main`.

```perl
sub helper($n) { "h$n" } class P { method m { helper(1) } } say P->new->m;
```
```
Undefined subroutine &P::helper called at 01-sub-from-method.pl line 3.
exit: 255
```

A field's default fails the same way (`01-sub-from-field.pl`, same error). With a `try`, perl prints `caught`:

```perl
sub helper($n) { "h$n" } class P { method m { try { helper(1) } catch ($e) { "caught" } } } say P->new->m;
```
```
caught
```

If a sub and a method share a name, perl calls the method as a plain function:

```perl
sub v() { "sub" } class P { method v { "meth" } method n { v() } } say P->new->n;
```
```
Cannot invoke method "v" on a non-instance at ... line 3.
exit: 255
```

Spelled out in full, `main::helper(1)` works and prints `h1`.

**What the proposal does:** it says only "a method is a sub to every rule of step 8". Today's resolver looks names up among the program's subs, so a build prints `h1` and `meth`.

**Way out:** refuse a call by name, inside a class's block, of any program sub, with a message naming `P::helper`. `main::helper(...)` could be taken in later, which agrees with perl. Roles need the same rule (finding 12).

## 2. WRONG: method names that perl will not install

The proposal lets a method be named with "perl's own words", except a short list. Two groups of names break.

**The thirteen builtins that `use v5.42` imports:** `true`, `false`, `weaken`, `unweaken`, `is_weak`, `blessed`, `refaddr`, `reftype`, `ceil`, `floor`, `is_tainted`, `trim` and `indexed`. A method with one of these names warns twice (D15), and is never installed:

```perl
class Range { field $lo :param :reader; field $hi :param :reader; method floor { $lo } method ceil { $hi } } my $r = Range->new(lo => 1, hi => 5); say $r->floor, "..", $r->ceil;
```
```
Prototype mismatch: sub floor ($) vs none at 02-method-floor-ceil.pl line 3.
Subroutine floor redefined at 02-method-floor-ceil.pl line 3.
Prototype mismatch: sub ceil ($) vs none at 02-method-floor-ceil.pl line 3.
Subroutine ceil redefined at 02-method-floor-ceil.pl line 3.
Can't locate object method "floor" via package "Range" at 02-method-floor-ceil.pl line 3.
exit: 255
```

All thirteen behave the same way. These seven work as method names: `stringify`, `created_as_string`, `created_as_number`, `inf`, `nan`, `export_lexically` and `load_module`. A reader of these names is not affected: `field $floor :reader` prints `2`.

**The special blocks:** `BEGIN`, `END`, `INIT`, `CHECK` and `UNITCHECK` become blocks, not methods:

```perl
class P { method END { "ok" } method call { $self->END } } say "start"; say P->new->call;
```
```
start
Can't locate object method "END" via package "P" at 02-method-end.pl line 3.
Cannot invoke method "END" on a non-instance.
END failed--call queue aborted.
exit: 22
```

`method BEGIN` dies while perl compiles; `INIT`, `CHECK` and `UNITCHECK` die before the program runs.

**What the proposal does:** accepts all of them, and prints `1..5` and `start ok`.

**Way out:** refuse both lists for `method` and `my method`. The table of names already holds them for subs.

## 3. WRONG: a `my method` takes every call of its name after it, and it is lexical

From its declaration to the end of the block, a `my method` takes every call of its name, builtin keywords included:

```perl
class P { my method say { "mine" } method m { say "x"; 1 } } P->new->m;
```
```
Cannot invoke method "say" on a non-instance at 03-my-method-say.pl line 3.
exit: 255
```
```perl
class P { my method length { "mine" } method m { $self->&length() . length("abc") } } say P->new->m;
```
```
Cannot invoke method "length" on a non-instance ... line 3.
exit: 255
```

`join`, `uc`, `push` and `trim` behave the same. It holds only after the declaration:

```perl
class P { method a { say "first"; 1 } my method say { "mine" } method b { say "second"; 1 } } P->new->a; P->new->b;
```
```
first
Cannot invoke method "say" ...
exit: 255
```

A public `method say` does not shadow the builtin.

**It is not seen above its declaration:**

```perl
class P { method a { $self->&b() } my method b { "b" } } say P->new->a;
```
```
Undefined subroutine &P::b called at ... line 3.
exit: 255
```

**`->&` is a direct call with no dispatch**, even of a public method:

```perl
class P { method a { $self->&b() } method b { "P.b" } } class Q :isa(P) { method b { "Q.b" } } say Q->new->a; say Q->new->b;
```
```
P.b
Q.b
```

**On another instance, perl checks the class.** `$o->&b()` with a `Q` instance dies `Cannot invoke a method of "P" on an instance of "Q"`; with another `P` it reads that instance's field (`n=2`).

**A `my method` and a public method of one name** give `Method b redefined`, and then `Can't locate object method "b"`.

**What the proposal does:** "a method seen only in its class's block". The obvious build makes it class-wide and leaves the builtins alone, so it prints `x`, `mine3` and `b`. If `->&` is read as dispatch, it prints `Q.b`.

**Way out:**
- Refuse a `my method` named with a perl word or one of finding 2's imports.
- Refuse a call by function syntax of a name that a `my method` in scope has.
- Refuse `->&NAME` before its `my method`, and `->&` of anything but a `my method`.
- Refuse a `my method` and a method of one name.
- Refuse `->&` on any invocant but `$self`, or check the class at run time.

## 4. WRONG: a method whose name is a class's name hides that class

T407 covers only a top-level sub. A method is a sub of its class's package, so inside `P`, after `method Q`, `Q->new` calls the method:

```perl
class Q { method m { "q" } } class P { method Q { "methQ" } method mk { Q->new->m } } say P->new->mk;
```
```
Cannot invoke method "Q" on a non-instance at 04-method-hides-class.pl line 3.
exit: 255
```

The same happens with `isa Q`: perl prints `died: Cannot invoke method "Q" on a non-instance`. A reader `field $Q :reader` does it, and so does a `my method Q`.

It depends on order: with `method Q` after `mk`, perl prints `q`.

A qualified name is looked up as a sub in the whole file:

```perl
class A { method B { "methB" } } class A::B { method m { "m" } } say A::B->new->m;
```
```
Cannot invoke method "B" on a non-instance ...
exit: 255
```

The same program with the use before `class A` prints `m`.

**What the proposal does:** prints `q`, `1` and `m`.

**Way out:**
- Refuse a method, reader, writer or `my method` named like a declared class, whatever the order.
- Refuse a method `N` of class `C` when a class `C::N` exists.

## 5. WRONG: class names share perl's namespace

```perl
class A { method v { "A" } } class v65 { method v { "v65" } } say v65->new->v;
```
```
A
```

Here is how other names fared, each run as `class NAME { method v { "ok" } } say NAME->new->v;`:

- **Die or do not compile:** `length`, `say`, `print`, `ref`, `true`, `ceil`, `open`, `if`, `my`, `q`, `m`, `qw`, `s`, `y`, `tr`, and `v1`.
- **Already loaded by the preamble:** `Carp` dies `Cannot create class Carp as it already has a non-empty @ISA`, and so does `Storable` under `use open`. `version` and `utf8` warn.
- **`builtin`:** `class builtin { method trim {..} }` gives the Prototype mismatch and redefined warnings.
- **`UNIVERSAL`:** gives its methods to every object. With `class Q {}`, `Q->new->v` prints `uv`.
- **`main`:** its methods become the program's subs, and perl dies.
- **`main::P`:** it is `P`.

After the preamble, `%main::` holds: CORE Carp DB DynaLoader Encode Exporter ExtUtils Fcntl IO Internals Log PerlIO Regexp Storable Tie UNIVERSAL XSLoader builtin bytes constant encoding experimental feature main mro open overload overloading parent re strict threads utf8 version warnings.

**Way out:**
- Every part of a class's name begins with a capital letter.
- It is not `main`, `UNIVERSAL`, `CORE`, `SUPER`, `DB`, `STDIN`, `STDOUT`, `STDERR`, `ARGV`, `ARGVOUT`, `ENV` or `INC`.
- No part of it is a package loaded by the end of the preamble.
- The C name made from it must be injective, so that `A::B` and `A_B` do not become one.

## 6. WRONG: `new` reads its keys first, and each value at its field's turn

```perl
my $v = "old";
class P { field $a = ($v = "new"); field $x :param :reader; }
say P->new(x => $v)->x;
```
```
new
```

The same holds when the field that changes `$v` is in a parent (`06-new-parent-field.pl`, `new`), and for an element (`9`). An element shifted out of the array is still the old scalar to perl:

```perl
my @a = (1, 2, 3);
class P { field $z = shift(@a); field $x :param :reader; }
say P->new(x => $a[0])->x, " @a";
```
```
1 2 3
```

The keys are read at once: `P->new($k => 5)`, with a field above that sets `$k = "y"`, prints `5 dy`. An `ADJUST` runs after every `:param`, so it changes nothing (`old new`).

**What the proposal does:** "checks the pairs, makes the instance, runs every field's initializer". The obvious build copies the pairs first, and prints `old`, `old` and `1`. Read late from a place in the array, the third is `2`, or memory that has moved.

**How today's compiler handles subs:** their arguments are places, read late (D73). A default that could change an earlier argument is refused:

```
s1.pl:4:1: a later part of the arguments of f can change @a, which an earlier part names: perl reads it after the change; take the value into a my first
```

perl itself panics on that program: `panic: attempt to copy freed scalar`.

**Way out:** agree.
- Hand `new` its values as places, and its keys as strings made at the call.
- Copy each value at its field's turn, in T400's order.
- D76's walk counts every field default before a `:param`, in the whole chain of parents, as a later part.

## 7. WRONG: `new`, readers and writers run code that the walks must see

Q3 teaches the walks about methods named `m`, but `new` is in no table. Its code is the field defaults and `ADJUST` blocks of the class and its parents. For `__CLASS__->new`, it is also the code of every class below. Readers and writers are generated, with no text to walk.

```perl
my $log = "a";
class P { ADJUST { $log .= "b" } method v { "c" } }
say $log . "-" . P->new->v;
```
```
ab-c
```

A field default `field $f = ($log .= "b")` also prints `ab-c`. These print what a build without the walk would not:

- `my @a = (1); class P { ADJUST { $a[0] = 9 } ... } say $a[0], P->new->v;` prints `9c`.
- `__CLASS__->new` in `P`, with a subclass `Q` whose `ADJUST` appends to `$log`, called on a `Q` object, prints `abb-c`.
- A writer: `method go { $x . "-" . ref($self->set_x("b")) . $x }` prints `b-Pb`.

Today the compiler refuses the sub form: "a later piece of a concatenation calls v, which can change $log, which an earlier piece reads". A build without the walk prints `a-c`, `1c`, `ab-c` and `a-Pa`.

**Way out:** say it in the proposal, and test each one.
- `NAME->new` is a call of every field default and `ADJUST` of NAME and its parents.
- `__CLASS__->new` written in class C is that, for C and every class below C.
- A reader reads its field, and a writer stores to it.

## 8. WRONG: the invocant is read at the call, in every shape D14 knows

```perl
class P { field $n :param :reader; method m($x) { "$n:$x" } } my @a = (P->new(n=>1)); say $a[0]->m(($a[0] = P->new(n=>2)) ? "x" : "y");
```
```
2:x
```

A chain, a hash element and `$$r` also print `2:x`; `//`, `? :` and an assignment print `2`.

**What the proposal does:** it names only a variable invocant. An element worked out first prints `1:x`. Today's compiler refuses `f($a[0], ($a[0]=5) ? 1 : 0)`.

**Way out:** the invocant is the call's first argument, for D14 and for every walk.

## 9. Ambiguous: fields and `$self` are lexical

A field is seen from its declaration on:

```perl
my $x = "file"; class P { method m { $x } field $x = "field"; method n { $x } } my $p = P->new; say $p->m, " ", $p->n;
```
```
file field
```

With no file variable, perl stops with `Global symbol "$x"`. A field's default reads a file variable named like a field declared below it (`5 1`).

`$self` can be declared over, silently:
- `method m($self) { $self }`, called with 5, prints `5`.
- `my $self = 3` in a method prints `3`.
- `field $self = 1; method m { $self }` prints `P=OBJECT(0x...)`.

A parameter or a `my` hides a field without a warning.

**Way out:** agree on the order, as the resolver does for `my`s. Refuse `$self` as a parameter, a `my`, or a field.

## 10. Ambiguous: what `SUPER::` is relative to

`SUPER` is the parent of the class where the method is written:

```perl
class A { method k { "A" } } class B :isa(A) { method k { "B" } method m { $self->SUPER::k() } } class C :isa(B) { } say C->new->m; say B->new->m;
```
```
A
A
```

Taking the parent of the object's class gives `B` on the first line.

- With another invocant, it is still the class where it is written: `$o->SUPER::m` in `C` dies `... via package "C"`.
- `SUPER::new` makes the parent's class (`A`).
- `B->new->A::m` prints `A`: a qualified name skips dispatch.

**Way out:** say how `SUPER::` is resolved, and that it is resolved as the program compiles. Refuse it on any invocant but `$self`, refuse `SUPER::new`, and refuse `->NAME::NAME` other than `SUPER`.

## 11. Ambiguous: `\` of a scalar field, `\$self`, and `ref \$o`

The reference to a scalar field is the same every time:

```perl
class P { field $x = 1; method r { \$x } method x { $x } } my $p = P->new; my $q = P->new; ${$p->r} = 5; say $p->x, $q->x; my $r1 = $p->r; my $r2 = $p->r; say $r1 == $r2 ? "same" : "diff";
```
```
51
same
```

So 13c's "a new cell each time its `my` is reached" is wrong for a field: the instance holds the cell from construction.

`\$self` gives the variable itself: `my $r = \$self; $$r = Q->new; $self->who` prints `Q`. Refuse it, as 13c refuses `\` of a loop's variable.

`ref \$o` prints `REF`, and `ref $$r` prints `P`. `reftype` gives `REF` for `\$o`, and `ARRAY`, `HASH` and `SCALAR` for the others; `blessed([1])` is undef.

**The runtime risk:** the runtime spells "is a reference" by three tags in about ten places (`rt.c` 381, 412, 595, 1136, 1148 and 1204; `unwind.c` 91, 121 and 170; `strfn.c` 70). Nearly all fault for a tag they do not know. `rt_ref` (`ref.c` 145) does not: it would print `SCALAR` without a fault if the new tag is missed. Test `ref \$o`, and `blessed` and `reftype` of every kind of value.

## 12. 17b: `SUPER::` and a sub's name in a role are the role's package

Under the roles perl:

- `role R { method m { "R" . $self->SUPER::m() } }`, with `class B :isa(A) :does(R)`, dies `Can't locate object method "m" via package "R"`.
- `helper()` in a role dies `Undefined subroutine &R::helper`.

If 17b compiles a role's method once per class, and 17a's `SUPER` means the parent of that class, the first prints `RA`. Refuse `SUPER::` in a role, and apply finding 1's rule to roles.

## 13. Attribute lexing

- `:param (y)` is a syntax error.
- Blanks inside the brackets are trimmed: `:param( y)` is `y`.
- `:param(  )` names the empty string, so `x => 3` is `Unrecognised`; `:param()` takes the default name.
- `:reader :reader(q)` makes two readers.
- `: param` is `:param`.

Refuse a blank before or inside an attribute's brackets, empty brackets, and a repeated attribute.

## 14. When the constructor's faults come

- An odd count is warned before anything runs.
- A missing `:param` is found at its field's turn: perl prints `fieldA`, then dies.
- An unknown name is found after every `ADJUST`: perl prints `fieldA`, `fieldB` and `adjust`, then `Unrecognised parameters ... y`.

The proposal does not say when each fault comes. Say "before anything runs", which stops earlier and is allowed, and write the fault tests that way.

## 15. D150 and a field over several lines

`field $y :param` on line 4, with `= die "no y";` on line 5, dies `no y at ... line 4.` A field's declaration is a statement for D150.

## 16. The root class's table

If D162's `Object` gives a program's classes any method, every class's table answers to that name. Then `$o->that` runs where perl dies, and "a name no class has is refused" stops refusing it. The proposal should say that the core gives nothing to dispatch to, and test it.

## 17. Holes in the test plan

- **perl segfaults (exit 139)** on `grep { $self->drop } @a`, where `drop` shifts the field `@a`. That is T194's kin: no fault test may ask perl for it.
- **A good `same` test:** a parent's `ADJUST` dispatching to the child's method, which sees the child's fields already made, prints `B.m v=5`.
- **Refusals, not the model:** findings 1 to 5 belong in `step17a-refusals.py`. `t/models/obj.py` cannot write them.
- **The oracle's reading rule:** a reader of a hash field gives its pairs in D27's order, so its test is a `new` test. The reading rule cannot see an order shown through `$p->h`.
- **Construction under `CURLY_GC_STRESS=1`:** the instance must be in a slot while its fields are made.
- **Nested construction** counts against D68's limit.
- **The pragma's place:** perl takes `use experimental 'class'` after other statements, before the first class. The proposal does not say where it goes.
- **C names:** a method may be named `int`, `return` or `main`, so a method's C name needs a prefix, and class names need an injective mangling.
