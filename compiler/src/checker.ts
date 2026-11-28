// The refusals that are rules of the language and not of its grammar
// (D29): a tree perl would accept and the language doesn't. It returns
// nothing; a tree that comes through is a program.
import { refuse } from './errors.ts';
import { BASED_MAX, DECIMAL_MAX_LENGTH, INT_MAX, PRAGMAS, VERSION, infixOp, prefixOp } from './names.ts';
import type { Chain, Class, Deref, Expr, My, Pragma, Program, Sderef, Stmt, Sub, Var } from './ast.ts';
import type { Resolution } from './resolver.ts';
import { handsOn, isCall, loneRange } from './shapes.ts';
import type { Call } from './shapes.ts';
import { checkFormat } from './format.ts';
import type { Gives } from './shapes.ts';

// What the checks need of the whole program (D20): the names, and for
// each sub the file variables a call of it can change, its own
// assignments and steps and those of every sub it calls (D69).
// `defaults` is the same for a sub's defaults alone, which run while its
// arguments are still being taken (T144, T149).
type World = { names: Resolution; changed: readonly ReadonlySet<number>[]; defaults: readonly ReadonlySet<number>[] };

// Where an expression stands: where one value is wanted, or where a list
// is (D80).
type Ctx = 'scalar' | 'list';

// What references reach (step 13a; D109): one more name in every walk
// over names, beside the declarations, which are numbered from 0. Every
// read through a reference names it, every store through one changes it,
// and a variable whose reference is taken anywhere is named and changed
// under it as well as under its own name.
const REACH = -1;
// And a part of it, the scalars references reach (step 13c): what a store
// through the scalar through a reference changes, and a store to a scalar
// variable whose reference is taken. A store through an element or a
// whole container through a reference changes what references reach and
// no scalar of it, since an element has no reference of its own (D110):
// so a loop over a scalar through a reference is refused only for what may
// change a scalar (D77, T347).
const CELLS = -2;

// The innermost head of an element through references: a scalar variable,
// an element of a named array or hash, or some other expression.
const chainBase = (c: Chain): Expr => (c.head.kind === 'chain' ? chainBase(c.head) : c.head);
// How many arrows (said or left out) a chain has.
const links = (c: Chain): number => (c.head.kind === 'chain' ? links(c.head) + 1 : 1);
// What a chain works out on its way, in order: its base when that is
// worked out, and every index or key.
const chainParts = (c: Chain): Expr[] => {
    const head = c.head.kind === 'chain' ? chainParts(c.head) : c.head.kind === 'elem' ? [c.head.index] : c.head.kind === 'var' ? [] : [c.head];
    return [...head, c.index];
};

// What the whole container through a reference works out on its way (step
// 13b), as a chain's last link would: its head's parts.
// (The scalar through a reference is the same, step 13c.)
const derefParts = (d: Deref | Sderef): Expr[] =>
    d.head.kind === 'chain' ? chainParts(d.head) : d.head.kind === 'elem' ? [d.head.index] : d.head.kind === 'var' ? [] : [d.head];
// The scalar variable a store through the whole container may make, if
// it starts from one (T248, T249).
const derefBase = (d: Deref | Sderef): Expr => (d.head.kind === 'chain' ? chainBase(d.head) : d.head);
// Whether a builtin through a reference makes what it goes through, as
// perl does: `push`, `unshift` and `splice` (T248).
const makesWhole = (e: Expr): boolean => e.kind === 'arrayop' && e.deref !== undefined && (e.op === 'push' || e.op === 'unshift' || e.op === 'splice' || e.op === '$#=');

// The expressions an expression is made of, in the order they are worked
// out.
const parts = (e: Expr): readonly Expr[] =>
    e.kind === 'chain' ? [e.head, e.index]
    : e.kind === 'deref' || e.kind === 'sderef' ? [e.head]
    : e.kind === 'anon' ? e.items
    : e.kind === 'hashop' && e.chain !== undefined ? [e.chain]
    // (Through a reference, a builtin's or a slice's container: a `push`'s
    // before what it adds, a slice's after its indexes, as perl has them.)
    : e.kind === 'arrayop' && e.deref !== undefined ? [e.deref, ...e.args]
    : e.kind === 'hashop' && e.deref !== undefined ? [...(e.keys ?? []), e.deref]
    : e.kind === 'slice' && e.deref !== undefined ? [...e.indexes, e.deref]
    : e.kind === 'unary' ? [e.operand]
    : e.kind === 'binary' ? [e.left, e.right]
    : e.kind === 'ternary' ? [e.test, e.then, e.else]
    : e.kind === 'apply' || e.kind === 'invoke' || e.kind === 'arrayop' || e.kind === 'listop' ? e.args
    // A call through a reference works out its arguments, then what stands
    // before the arrow (step 14; T370, D166). A sub with no name is a
    // value, made where it stands: its body is its own function's.
    : e.kind === 'callref' ? [...e.args, e.head]
    // A method call works out its invocant, then its arguments (T405,
    // T429); `new` its arguments; `isa` its left side (step 17a).
    : e.kind === 'methcall' ? [e.invocant, ...e.args]
    : e.kind === 'new' ? e.args
    : e.kind === 'isa' ? [e.left]
    : e.kind === 'assign' ? [e.value, e.target]
    : e.kind === 'step' ? [e.target]
    : e.kind === 'elem' ? [e.index]
    : e.kind === 'hashop' ? (e.keys ?? (e.key === undefined ? [] : [e.key]))
    : e.kind === 'list' ? e.items
    : e.kind === 'slice' ? [...e.indexes, ...(e.items ?? [])]
    : e.kind === 'listassign' ? [e.value, ...e.targets]
    // A block is part of its `map` or `grep`: what it changes, they
    // change, and what it reads, they read (D76 goes through a block).
    : e.kind === 'binder' ? [...e.items, ...within(e.body)]
    : e.kind === 'sort' ? [...e.items, ...within(e.body ?? [])]
    // An interpolated string is a value, made where it stands (T196, D95):
    // for what a row of dots reads, what a list names and what a loop's
    // list holds, it has no parts. (`children` has them, to be checked.)
    : [];

// Every expression the statements of a block hold.
const within = (body: readonly Stmt[]): Expr[] => {
    const found: Expr[] = [];
    body.forEach(s => expressions(s, e => found.push(e)));
    return found;
};

const checkLiteral = (e: Expr): void => {
    if (e.kind !== 'int' && e.kind !== 'num') return;
    // perl reads `010` as octal, 8, doesn't compile `08`, and reads
    // `00.5` as two numbers joined (T24, T78). Octal is `0o10` (D38).
    if (/^0[0-9_]/.test(e.text)) {
        refuse(`${e.text} starts with a zero: perl reads that as octal, which the language writes 0o17`, e.pos);
    }
    if (e.kind === 'num') {
        // perl reads a decimal into a buffer of its own, and stops the
        // compile at 250 characters, underscores not counted (T91).
        if (e.text.replaceAll('_', '').length > DECIMAL_MAX_LENGTH) {
            refuse(`a number of more than ${DECIMAL_MAX_LENGTH} characters: perl refuses it as too long`, e.pos);
        }
        // perl makes it an infinity, in silence (T81); a Num is finite (D37).
        if (!Number.isFinite(e.value)) refuse(`${e.text} is past the largest float`, e.pos);
        return;
    }
    if (/^0[xXbBoO]/.test(e.text)) {
        if (e.value > BASED_MAX) refuse(`${e.text} is past 32 bits, where perl warns that a literal is not portable`, e.pos);
        return;
    }
    // perl carries on past here as an unsigned integer and then a float,
    // in silence (D23, T81). So -2^63 can't be written as a literal with
    // a minus: its digits are past the largest.
    if (e.value > INT_MAX) refuse(`${e.text} is past the largest integer, ${INT_MAX}`, e.pos);
};

// An expression behind any unary plus, which does nothing in perl either.
const plain = (e: Expr): Expr => (e.kind === 'unary' && prefixOp(e.op)?.rt === undefined ? plain(e.operand) : e);

// Whether perl may fold an expression to a constant as it compiles: one
// with no variable in it, and one whose variables are all behind a test
// that folds, `0 && $y`, `1 ? 2 : $y` (T112). perl folds `1 && $y` to
// `$y`, which is no constant: this says yes to a little more than perl
// does, with no folder of its own.
const folds = (e: Expr): boolean =>
    e.kind === 'var' || e.kind === 'my' || e.kind === 'assign' || e.kind === 'step' || e.kind === 'invoke' || e.kind === 'interp' ? false
    // (A sub's reference, and a call through one: perl does not warn of
    // `if (my $f = sub { 1 })`, step 14.)
    : e.kind === 'anonsub' || e.kind === 'subref' || e.kind === 'cursub' || e.kind === 'callref' ? false
    // (An object, and what is asked of one, step 17a.)
    : e.kind === 'methcall' || e.kind === 'new' || e.kind === 'curclass' || e.kind === 'isa' ? false
    // (A new container, and a reference, are made as the program runs:
    // perl does not warn of `if (my $r = [1])`.)
    : e.kind === 'chain' || e.kind === 'anon' || e.kind === 'ref' || e.kind === 'deref' || e.kind === 'sderef' ? false
    // (An array, an element, and what works on one are no constants.)
    : e.kind === 'array' || e.kind === 'myarray' || e.kind === 'elem' || e.kind === 'lastindex' || e.kind === 'arrayop' || e.kind === 'hashop' || e.kind === 'listassign' ? false
    : e.kind === 'slice' && e.name !== undefined ? false
    : e.kind === 'ternary' ? folds(e.test)
    : e.kind === 'binary' && infixOp(e.op)?.when ? folds(e.left)
    : parts(e).every(folds);

// The names an expression reads, and the ones it changes: by name, which
// is a little more than by declaration, and errs toward refusing.
const reads = (e: Expr, into = new Set<string>()): Set<string> => {
    if (e.kind === 'var' || e.kind === 'my') into.add(e.name);
    parts(e).forEach(p => reads(p, into));
    return into;
};
const changes = (e: Expr, into = new Set<string>()): Set<string> => {
    if ((e.kind === 'assign' || e.kind === 'step') && (e.target.kind === 'var' || e.target.kind === 'my')) into.add(e.target.name);
    // A store through a chain may make the variable it starts from (T249).
    if ((e.kind === 'assign' || e.kind === 'step') && e.target.kind === 'chain') {
        const base = chainBase(e.target);
        if (base.kind === 'var') into.add(base.name);
    }
    // And a store to the whole container through one (step 13b), and to
    // the scalar through one (step 13c).
    const whole = (e.kind === 'assign' || e.kind === 'step') && (e.target.kind === 'deref' || e.target.kind === 'sderef') ? e.target : makesWhole(e) ? (e as { deref: Deref }).deref : undefined;
    if (whole !== undefined && derefBase(whole).kind === 'var') into.add((derefBase(whole) as Var).name);
    parts(e).forEach(p => changes(p, into));
    return into;
};

// ---- lists (D76, D80)

// A string that is a number, as D40 has it and perl takes in silence.
const NUMERIC_STRING = /^[ \t\n\r\f\v]*[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?[ \t\n\r\f\v]*$/;

// A range, and a list repeat: `(LIST) x N`, which is one only where a list
// is wanted, its left side in brackets (T101).
const isRange = (e: Expr): boolean => e.kind === 'binary' && infixOp(e.op)?.range === true;
const isRepeat = (e: Expr): boolean => e.kind === 'binary' && infixOp(e.op)?.list === true && (e.left.kind === 'list' || e.left.bracketed === true);

// What is a list where a list is wanted: more values than one, or fewer.
// (A slice of a list with no values is none, whatever its indexes: T164.)
const listy = (in_: Expr): boolean => {
    const e = plain(in_);
    return e.kind === 'array' || e.kind === 'myarray' || (e.kind === 'deref' && !e.last) || e.kind === 'list' || isRange(e) || isRepeat(e)
        || e.kind === 'slice'
        || (e.kind === 'arrayop' && e.op === 'splice')
        || (e.kind === 'listop' && e.op === 'reverse')
        || (e.kind === 'hashop' && (e.op === 'keys' || e.op === 'values' || e.keys !== undefined))
        || e.kind === 'binder' || e.kind === 'sort'
        || (e.kind === 'ternary' && (listy(e.then) || listy(e.else)))
        || (e.kind === 'binary' && infixOp(e.op)?.when !== undefined && listy(e.right));
};

// Whether a call is of a sub that gives a list back (D18); one through a
// reference is of any sub a reference can be to (D163).
// A method call is of any method of its name (D172); `new` gives one value.
const gives = (w: World): Gives => call => (call.kind === 'invoke' ? w.names.lists[w.names.calls.get(call)!] === true
    : call.kind === 'callref' ? w.names.targets.some(t => w.names.lists[t] === true)
    : call.kind === 'new' ? false
    : calleeTargets(w, call).some(t => w.names.lists[t] === true));

// Every function a call may run (D163, D172, D178).
const calleeTargets = (w: World, e: Call): readonly number[] =>
    e.kind === 'invoke' ? [w.names.calls.get(e)!] : e.kind === 'callref' ? w.names.targets : w.names.targetsOf.get(e)!;

// What a call can change (D69), and what its defaults can (T144): of the
// sub it calls, or for a call through a reference of any sub a reference
// can be to (step 14; D163).
// (`new`'s defaults are its fields' defaults, the functions of the
// classes' fields, which copy each argument at its field's turn: D178.)
const calleeChanges = (w: World, e: Call): ReadonlySet<number> => new Set(calleeTargets(w, e).flatMap(t => [...w.changed[t]!]));
const calleeDefaults = (w: World, e: Call): ReadonlySet<number> =>
    e.kind === 'new' ? new Set(calleeTargets(w, e).filter(t => w.names.subs[t - 1]!.method?.how === 'init').flatMap(t => [...w.changed[t]!]))
    : new Set(calleeTargets(w, e).flatMap(t => [...w.defaults[t]!]));
const callName = (e: Call): string => (e.kind === 'invoke' ? e.name : e.kind === 'callref' ? 'a sub through a reference' : e.kind === 'new' ? `${e.cls ?? '__CLASS__'}->new` : `the method ${e.name}`);

// A declaration that is named or changed, and what references reach with
// it when its reference is taken anywhere (D109).
const addId = (w: World, into: Set<number>, id: number): void => {
    into.add(id);
    if (w.names.taken.has(id)) into.add(REACH);
};

// What making the hops of a store through a chain changes (T248, T249,
// D114): the variable it starts from, or the named array or hash whose
// element it starts from, which a hop that is undef is made in; and what
// references reach, when a hop after the first is made.
const making = (w: World, c: Chain | Deref | Sderef, into = new Set<number>()): Set<number> => {
    // The whole container through a reference (step 13b) is made as a
    // chain's last link would be: in its head, or in what its head's chain
    // reaches. So is the scalar through one (step 13c).
    if (c.kind === 'deref' || c.kind === 'sderef') {
        const head = c.head;
        if (head.kind === 'var' || head.kind === 'elem') addId(w, into, w.names.of.get(head)!);
        if (head.kind === 'chain') {
            making(w, head, into);
            into.add(REACH);
        }
        return into;
    }
    const base = chainBase(c);
    if (base.kind === 'var' || base.kind === 'elem') addId(w, into, w.names.of.get(base)!);
    if (links(c) >= 2) into.add(REACH);
    return into;
};

// What a node changes by itself: the variable it assigns or steps, the
// array whose element it stores or whose size it changes. A store through
// a reference changes what references reach, and what its hops are made
// in (step 13a). `direct`: only what the node assigns by name, as a loop's
// read-only variable asks (D17); a store through one is a store to what it
// points at.
const changesItself = (w: World, e: Expr, direct = false): number[] => {
    const id = (x: Expr): number => w.names.of.get(x)!;
    if ((e.kind === 'assign' || e.kind === 'step') && e.target.kind === 'sderef') return direct ? [] : [REACH, CELLS, ...making(w, e.target)];
    if ((e.kind === 'assign' || e.kind === 'step') && (e.target.kind === 'chain' || e.target.kind === 'deref')) return direct ? [] : [REACH, ...making(w, e.target)];
    if (e.kind === 'assign' || e.kind === 'step') return [id(e.target)];
    // Through a reference (step 13b): what it reaches, and, for `push`,
    // `unshift` and `splice`, what the container is made in.
    if (e.kind === 'arrayop' && e.op !== 'scalar' && e.deref !== undefined) return direct ? [] : makesWhole(e) ? [REACH, ...making(w, e.deref)] : [REACH];
    if (e.kind === 'arrayop' && e.op !== 'scalar') return [id(e)];
    if (e.kind === 'hashop' && e.op === 'delete' && (e.chain !== undefined || e.deref !== undefined)) return direct ? [] : [REACH];
    // A `delete` changes its hash: perl reads freed values where one
    // follows a part that names the hash (D102).
    if (e.kind === 'hashop' && e.op === 'delete') return [id(e)];
    if (e.kind === 'listassign') {
        return e.targets.filter(t => t.kind !== 'constant').flatMap(t => (t.kind === 'slice' && t.deref !== undefined ? (direct ? [] : [REACH, ...making(w, t.deref)])
            : t.kind === 'sderef' ? (direct ? [] : [REACH, CELLS, ...making(w, t)])
            : t.kind === 'deref' ? (direct ? [] : [REACH, ...making(w, t)])
            : t.kind !== 'chain' ? [id(t)] : direct ? [] : [REACH, ...making(w, t)]));
    }
    return [];
};

// Everything working an expression out can change: itself, what it holds,
// and the subs it calls (D69).
const changeSet = (w: World, e: Expr, into = new Set<number>()): Set<number> => {
    changesItself(w, e).forEach(id => addId(w, into, id));
    if (isCall(e)) calleeChanges(w, e).forEach(id => into.add(id));
    parts(e).forEach(p => changeSet(w, p, into));
    return into;
};

// What a part of a list or an expression *names*: the containers perl
// would have carried, and read late (T149, T157). An element, a slice, an
// array, `$#a`; and, where the part is copied into a list (`scalars`), a
// scalar variable that is itself the part. Through brackets, a unary
// plus, both branches of `? :`, either side of `||` and its kin, a list
// in a list, a list repeated, and a slice of a list.
const named = (w: World, in_: Expr, scalars: boolean, into = new Set<number>()): Set<number> => {
    const e = plain(in_);
    const id = (x: Expr): void => { addId(w, into, w.names.of.get(x)!); };
    // An element through a reference names what references reach, and
    // what its chain starts from, which a later part may replace: perl
    // prints a freed value there (T235, T236).
    const chain = (c: Chain): void => {
        into.add(REACH);
        const base = chainBase(c);
        if (base.kind === 'var' || base.kind === 'elem') id(base);
        else named(w, base, true, into);
    };
    // The whole container through a reference names what its head does,
    // as a chain's last link would (step 13b), and what references reach.
    const whole = (d: Deref | Sderef): void => {
        into.add(REACH);
        if (d.head.kind === 'var' || d.head.kind === 'elem') id(d.head);
        else if (d.head.kind === 'chain') chain(d.head);
        else named(w, d.head, true, into);
    };
    if (e.kind === 'chain') chain(e);
    // The scalar through a reference is read where it stands, as an
    // element through one is (step 13c): perl reads it late, as the
    // variable it is (T346).
    else if (e.kind === 'deref' || e.kind === 'sderef') whole(e);
    else if ((e.kind === 'slice' || (e.kind === 'hashop' && e.op === 'values')) && e.deref !== undefined) whole(e.deref);
    else if ((e.kind === 'assign' || (e.kind === 'step' && e.before)) && e.target.kind === 'chain') chain(e.target);
    else if ((e.kind === 'assign' || (e.kind === 'step' && e.before)) && e.target.kind === 'sderef') whole(e.target);
    else if (e.kind === 'elem' || e.kind === 'array' || e.kind === 'lastindex') id(e);
    else if (e.kind === 'slice' && e.name !== undefined) id(e);
    // `values` are the hash's own, and `keys` are copies (T217, T218).
    else if (e.kind === 'hashop' && e.op === 'values') id(e);
    else if (e.kind === 'slice') e.items!.forEach(x => named(w, x, true, into));
    else if (e.kind === 'list') e.items.forEach(x => named(w, x, true, into));
    else if (e.kind === 'var' && scalars) id(e);
    else if ((e.kind === 'assign' || (e.kind === 'step' && e.before)) && e.target.kind === 'var' && scalars) id(e.target);
    // An assignment to an element, and `++$a[0]`, are the element itself
    // to perl, read late like any other (T213): `($a[0] = 5) + ($a[0] =
    // 7)` is 14. Here each is the value it stored, so it names its array.
    else if ((e.kind === 'assign' || (e.kind === 'step' && e.before)) && e.target.kind === 'elem') id(e.target);
    else if (e.kind === 'ternary') { named(w, e.then, scalars, into); named(w, e.else, scalars, into); }
    else if (e.kind === 'binary' && infixOp(e.op)?.when) { named(w, e.left, scalars, into); named(w, e.right, scalars, into); }
    else if (isRepeat(e) && e.kind === 'binary') named(w, e.left, true, into);
    // `reverse` hands on the containers it was given, as a list does
    // (T185, D87); `join` gives a value at once.
    else if (e.kind === 'listop' && e.op === 'reverse') e.args.forEach(x => named(w, x, true, into));
    // So does `grep`: what it keeps are the things it was given. `map`
    // copies what its block gives.
    else if (e.kind === 'binder' && e.op === 'grep') e.items.forEach(x => named(w, x, true, into));
    else if (e.kind === 'sort') e.items.forEach(x => named(w, x, true, into));
    return into;
};

const sigil = (w: World, id: number): string => (id === REACH ? 'what references reach' : id === CELLS ? 'a scalar that a reference reaches' : (w.names.isHash[id] ? '%' : w.names.isArray[id] ? '@' : '$') + w.names.names[id]);

// What a value is, where perl hands on the place itself and this copies it
// (step 13a): an element, an element through a reference (somewhere in what
// references reach), and with `scalars`, a scalar variable; through
// brackets, a unary plus, an assignment (which is its target), both
// branches of `? :` and both sides of `|| && //`, and the items of a list.
// Making a hop changes the place it is made in: so a value that is that
// place, taken before the hop is made, is not what perl stores (T249).
const aliases = (w: World, in_: Expr, scalars: boolean, into = new Set<number>()): Set<number> => {
    const e = plain(in_);
    if (e.kind === 'elem') addId(w, into, w.names.of.get(e)!);
    else if (e.kind === 'chain' || e.kind === 'sderef') into.add(REACH);
    else if (e.kind === 'var' && scalars) addId(w, into, w.names.of.get(e)!);
    else if ((e.kind === 'assign' || (e.kind === 'step' && e.before)) && e.target.kind !== 'array' && e.target.kind !== 'myarray') aliases(w, e.target, true, into);
    else if (e.kind === 'ternary') { aliases(w, e.then, scalars, into); aliases(w, e.else, scalars, into); }
    else if (e.kind === 'binary' && infixOp(e.op)?.when) { aliases(w, e.left, scalars, into); aliases(w, e.right, scalars, into); }
    else if (e.kind === 'list') e.items.forEach(x => aliases(w, x, true, into));
    return into;
};

// The hops of a store through `target` are made after `value` was taken:
// refused where making one changes what the value is (T249).
const checkMaking = (w: World, target: Chain | Deref | Sderef, value: Expr, scalars: boolean): void => {
    const is = aliases(w, value, scalars);
    const base = target.kind === 'deref' || target.kind === 'sderef' ? derefBase(target) : chainBase(target);
    for (const id of making(w, target)) {
        if (is.has(id)) refuse(`the store makes what ${base.kind === 'var' && id !== REACH ? sigil(w, id) + ' holds' : 'it goes through'}, which the right side has already taken: perl takes it after it is made; take the value into a my first`, target.pos);
    }
};

// D247: a list repeated by 1, or by a count perl folds, where a `? :`
// or a logical operator passes it, through brackets and the items of a
// list (T603).
const checkPassedRepeat = (in_: Expr): void => {
    const e = plain(in_);
    if (e.kind === 'list') return e.items.forEach(checkPassedRepeat);
    if (e.kind !== 'binary' || !isRepeat(e)) return;
    const count = plain(e.right);
    const written = (count.kind === 'int' && count.value !== 1n) || count.kind === 'num' || count.kind === 'str';
    if (!written && folds(count)) {
        refuse('a list repeated by 1, or by a count perl works out as it compiles, in a branch of ? : or after a logical operator: perl 5.42 loses its place there (D247); write the list once, or the count as a number', e.right.pos);
    }
};

// D246: perl takes each container of a chain before it works out the
// index or key after it, and holds no count on it while it does: an index
// that lets go of the container (an assignment to the variable the chain
// starts from, to the array or hash whose element it starts from, or
// through a reference to what holds it) leaves perl reading undef from a
// freed container or dying, `Modification of a read-only value attempted`,
// where the language would read or store what it took (T602). So an index
// or key may not change the variable or the array the chain starts from,
// nor, past the first container or from an element, what references reach.
const checkHops = (w: World, c: Chain): void => {
    const hops: Chain[] = [];
    for (let x: Expr = c; x.kind === 'chain'; x = x.head) hops.unshift(x);
    const base = hops[0]!.head;
    hops.forEach((hop, k) => {
        const held = new Set<number>();
        if (base.kind === 'var' || base.kind === 'elem') addId(w, held, w.names.of.get(base)!);
        if (k >= 1 || base.kind === 'elem') held.add(REACH);
        for (const id of changeSet(w, hop.index)) {
            if (held.has(id)) {
                refuse(`this ${hop.hash ? 'key' : 'index'} can change ${sigil(w, id)}, which holds the container it is ${hop.hash ? 'a key' : 'an index'} of: perl takes the container first, and reads or stores a freed one when the ${hop.hash ? 'key' : 'index'} lets go of it (D246); take the ${hop.hash ? 'key' : 'index'} into a my first`, hop.index.pos);
            }
        }
    });
};

// D76: of parts worked out in this order, a later one may not change what
// an earlier one names. `also` is what else runs after them all (a sub's
// defaults, for its arguments).
const checkOrder = (w: World, what: string, sequence: readonly Expr[], scalars: boolean, also?: { changes: ReadonlySet<number>; at: Expr }): void => {
    const seen = new Set<number>();
    const refused = (id: number, at: Expr): never =>
        refuse(`a later part of ${what} can change ${sigil(w, id)}, which an earlier part names: perl reads it after the change; take the value into a my first`, at.pos);
    for (const part of sequence) {
        if (seen.size > 0) {
            for (const id of changeSet(w, part)) if (seen.has(id)) refused(id, part);
        }
        named(w, part, scalars, seen);
    }
    if (also) for (const id of also.changes) if (seen.has(id)) refused(id, also.at);
};

// Where one value is wanted: what may not stand there (T151, T68, T168).
const checkOneValue = (w: World, e: Expr): void => {
    // (A new container where one value is wanted is a reference: no list.)
    if (e.kind === 'list') refuse(e.my ? 'my (...) where one value is wanted' : 'a list where one value is wanted: perl gives its last value, and warns of the others', e.pos);
    if (e.kind === 'myarray') refuse(`my ${e.hash ? '%' : '@'}${e.name} where one value is wanted`, e.pos);
    // `(LIST)[N]`, one index that is one value, is an element there.
    // perl's `sort` there is undef, with a warning (T178, D84).
    if (e.kind === 'sort') refuse('sort where one value is wanted: perl gives undef there, and warns', e.pos);
    // perl's `reverse` there joins its arguments and reverses the
    // characters (T178, D84).
    if (e.kind === 'listop' && e.op === 'reverse') refuse('reverse where one value is wanted: perl joins its arguments and reverses the characters there, which is another function', e.pos);
    if (e.kind === 'slice' && (e.name !== undefined || e.indexes.length !== 1 || listy(e.indexes[0]!) || handsOn(e.indexes[0]!, gives(w)))) refuse(`a slice where one value is wanted: perl gives its last element; write the element, ${e.hash ? '$h{...}' : '$a[...]'}`, e.pos);
    if (e.kind === 'hashop' && e.keys !== undefined) refuse('delete of a slice where one value is wanted: perl gives the last value it deleted; delete the element, or assign the list to an array', e.pos);
    if (isRange(e)) refuse("a range where one value is wanted: '..' is another operator to perl there", e.pos);
    if (e.kind === 'binary' && isRepeat(e) && e.left.kind === 'list') refuse(`a list on the left of '${e.op}' where one value is wanted: perl repeats its last value`, e.left.pos);
    if (e.kind === 'arrayop' && e.op === 'splice') refuse('splice where one value is wanted: perl gives the last element it removed; assign it to an array', e.pos);
};

// What an expression's parts are, each with where it stands.
const children = (e: Expr, ctx: Ctx): [Expr, Ctx][] => {
    const all = (es: readonly Expr[], c: Ctx): [Expr, Ctx][] => es.map(x => [x, c]);
    switch (e.kind) {
    case 'unary': return [[e.operand, prefixOp(e.op)?.rt === undefined ? ctx : 'scalar']];
    case 'binary':
        if (infixOp(e.op)?.when) return [[e.left, 'scalar'], [e.right, ctx]];
        if (ctx === 'list' && isRepeat(e)) return [[e.left, 'list'], [e.right, 'scalar']];
        return [[e.left, 'scalar'], [e.right, 'scalar']];
    case 'ternary': return [[e.test, 'scalar'], [e.then, ctx], [e.else, ctx]];
    case 'apply': return all(e.args, 'scalar');
    case 'invoke': return all(e.args, 'list');
    // Step 14 (a sub with no name is checked as a sub, by `checkExpr`).
    case 'callref': return [...all(e.args, 'list'), [e.head, 'scalar']];
    // Step 17a.
    case 'methcall': return [[e.invocant, 'scalar'], ...all(e.args, 'list')];
    case 'new': return all(e.args, 'list');
    case 'isa': return [[e.left, 'scalar']];
    case 'assign': return [[e.value, e.target.kind === 'array' || e.target.kind === 'myarray' || e.target.kind === 'deref' ? 'list' : 'scalar'], [e.target, 'list']];
    case 'step': return [[e.target, 'scalar']];
    case 'elem': return [[e.index, 'scalar']];
    // Step 13a.
    case 'chain': return [[e.head, 'scalar'], [e.index, 'scalar']];
    // Step 13b.
    case 'deref': return [[e.head, 'scalar']];
    // Step 13c.
    case 'sderef': return [[e.head, 'scalar']];
    case 'anon': return all(e.items, 'list');
    case 'hashop': return e.chain !== undefined ? [[e.chain, 'scalar']] : [...(e.keys !== undefined ? all(e.keys, 'list') : e.key === undefined ? [] : [[e.key, 'scalar']] as [Expr, Ctx][]), ...(e.deref !== undefined ? [[e.deref, 'list']] as [Expr, Ctx][] : [])];
    // A string's pieces: an array there is its values, not its count.
    case 'interp': return all(e.parts, 'list');
    case 'list': return all(e.items, 'list');
    case 'slice': return [...all(e.indexes, 'list'), ...all(e.items ?? [], 'list'), ...all(e.deref !== undefined ? [e.deref] : [], 'list')];
    case 'arrayop': return [...all(e.deref !== undefined ? [e.deref] : [], 'list'), ...(e.op === '$#=' ? all(e.args, 'scalar') : e.op === 'splice' ? [...all(e.args.slice(0, 2), 'scalar'), ...all(e.args.slice(2), 'list')] : all(e.args, 'list'))];
    // `join`'s separator is one value (T182).
    // A block's statements are checked as statements, by `checkExpr`.
    case 'binder': return [];
    case 'sort': return [];
    case 'listop': return e.op === 'join' || e.op === 'sprintf' ? [...all(e.args.slice(0, 1), 'scalar'), ...all(e.args.slice(1), 'list')] : all(e.args, 'list');
    case 'listassign': return [[e.value, 'list'], ...all(e.targets, 'list')];
    default: return [];
    }
};

// The calls of the program's subs in an expression, and its variables.
const invokes = (e: Expr, into: Call[] = []): Call[] => {
    if (isCall(e)) into.push(e);
    parts(e).forEach(p => invokes(p, into));
    return into;
};
const variables = (e: Expr, into: Expr[] = []): Expr[] => {
    // (An array's count, `$#a` and what `pop` gives are values at once.)
    // An element through a reference is read late too (T235).
    // (And the scalar through one, step 13c.)
    if (e.kind === 'var' || e.kind === 'my' || e.kind === 'elem' || e.kind === 'chain' || e.kind === 'sderef') into.push(e);
    parts(e).forEach(p => variables(p, into));
    return into;
};

// perl joins a row of dots as one operation, and reads every piece when
// it runs: `$x . "a" . ($x = 5)` is `5a5`, where the first dot alone
// would have made `3a` (T117). How far a row reaches turns on what perl
// folds away as it compiles (`(1 ? $x . "a" : 0) . ($x = 5)` is a row
// too), and on its length. So a later piece of a concatenation may not
// change a variable an earlier piece reads (D57); a piece is found
// through brackets, a unary plus, and both sides of whatever gives one
// operand or the other.
const pieces = (e: Expr): Expr[] => {
    const p = plain(e);
    if (p.kind === 'binary' && (infixOp(p.op)?.concat || infixOp(p.op)?.when)) return [...pieces(p.left), ...pieces(p.right)];
    if (p.kind === 'ternary') return [p.test, ...pieces(p.then), ...pieces(p.else)];
    return [p];
};
// What an expression may be worth, behind brackets, a unary plus, and
// whatever gives one operand or the other (which perl may have folded
// away).
const wholes = (e: Expr): Expr[] => {
    const p = plain(e);
    if (p.kind === 'binary' && infixOp(p.op)?.when) return [...wholes(p.left), ...wholes(p.right)];
    if (p.kind === 'ternary') return [...wholes(p.then), ...wholes(p.else)];
    return [p];
};

// `$t .= ($u = $x . $z);` never assigns `$u`, in perl 5.42 and 5.38: it
// makes one operation of the `.=` and the dot, and the `=` between them
// is lost (T129). So the right side of `.=` may not be an assignment of
// a concatenation. Nor of an interpolated string, which is one to perl,
// however many pieces it has (T198, T212); a string that is one variable,
// one array, one element, one slice or one `$#a` and nothing else is
// assigned.
const checkLostAssignment = (e: Expr): void => {
    if (e.kind !== 'assign' || !infixOp(e.op)?.concat) return;
    for (const w of wholes(e.value)) {
        // (To a `my` it is made; and a `my` may not stand there.)
        // (perl assigns through a reference there: step 13a.)
        const plainAssign = w.kind === 'assign' && (w.target.kind === 'var' || w.target.kind === 'elem') && infixOp(w.op)?.rt === undefined && infixOp(w.op)?.when === undefined;
        const name = w.kind === 'assign' && (w.target.kind === 'var' || w.target.kind === 'elem') ? w.target.name : '';
        if (w.kind === 'assign' && plainAssign && wholes(w.value).some(v => v.kind === 'binary' && infixOp(v.op)?.concat)) {
            refuse(`'${e.op}' of an assignment of a concatenation: perl makes one operation of the three and never assigns $${name}; make the assignment a statement of its own`, w.pos);
        }
        if (w.kind === 'assign' && plainAssign && wholes(w.value).some(v => v.kind === 'interp' && v.parts.length > 1)) {
            refuse(`'${e.op}' of an assignment of an interpolated string: perl makes one operation of them and never assigns $${name}; make the assignment a statement of its own`, w.pos);
        }
    }
};

const checkConcat = (w: World, e: Expr): void => {
    checkLostAssignment(e);
    // The left of `.=` is the first piece: a variable, read late. An
    // element there has its index worked out before the row is.
    const row = e.kind === 'binary' && infixOp(e.op)?.concat ? pieces(e)
        : e.kind === 'assign' && infixOp(e.op)?.concat && e.target.kind !== 'elem' && e.target.kind !== 'chain' ? [e.target, ...pieces(e.value)]
        : e.kind === 'assign' && infixOp(e.op)?.concat ? pieces(e.value)
        : [];
    const read = new Set<string>();
    // The same through a call (D69, T132): the declarations the earlier
    // pieces read, and the file variables a sub called in this piece can
    // change.
    const readIds = new Set<number>();
    for (const piece of row) {
        for (const name of changes(piece)) {
            if (read.has(name)) {
                refuse(`a later piece of a concatenation changes $${name}, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the change a statement of its own`, piece.pos);
            }
        }
        for (const call of invokes(piece)) {
            for (const id of calleeChanges(w, call)) {
                if (readIds.has(id)) {
                    refuse(`a later piece of a concatenation calls ${callName(call)}, which can change ${sigil(w, id)}, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the call a statement of its own`, call.pos);
                }
            }
        }
        // And an array an earlier piece reads, changed by this one itself;
        // and what references reach (D109).
        for (const id of changeSet(w, piece)) {
            if (readIds.has(id) && (id === REACH || w.names.isArray[id])) {
                refuse(`a later piece of a concatenation changes ${sigil(w, id)}, which an earlier piece reads: perl joins the pieces as one operation and reads each late; make the change a statement of its own`, piece.pos);
            }
        }
        reads(piece, read);
        variables(piece).forEach(v => (v.kind === 'chain' || v.kind === 'sderef' ? readIds.add(REACH) : addId(w, readIds, w.names.of.get(v)!)));
    }
};

// A `=` whose right side is a constant, where its value is tested for
// truth: `if ($x = 5)` (D53). perl warns `Found = in conditional` when
// the right side is a constant after folding what it can, `$x = 0 && $y`
// too (T112); this is that and a little more. `tested` goes down
// through what hands a test on: a unary plus, `!` and `not` (perl takes
// the `!` of a condition away and tests the other way), the right of an
// operator that gives one operand or the other, and the branches of `? :`.
const tested = (in_: Expr): void => {
    const e = plain(in_);
    if (e.kind === 'unary' && prefixOp(e.op)?.tests) return tested(e.operand);
    if (e.kind === 'assign' && infixOp(e.op)?.rt === undefined && infixOp(e.op)?.when === undefined && folds(e.value)) {
        refuse(`'${e.op}' where a value is tested, with nothing but a constant on its right: perl warns that == was meant`, e.pos);
    }
    // Both operands: under a `!`, perl has the left one tested too.
    if (e.kind === 'binary' && infixOp(e.op)?.when) {
        tested(e.left);
        tested(e.right);
    }
    if (e.kind === 'ternary') {
        tested(e.then);
        tested(e.else);
    }
};

// perl warns of a slice of one, by how the index is spelled: `Scalar value
// @a[0] better written as $a[0]` (T167), and `@h{a}` so (T221). Refused a
// little more widely.
const checkSliceOfOne = (e: Expr): void => {
    // (perl does not warn of one through a reference: step 13b.)
    if (e.kind !== 'slice' || e.name === undefined || e.deref !== undefined || e.indexes.length !== 1) return;
    const one = e.indexes[0]!;
    if (listy(one) || one.kind === 'invoke' || one.bracketed) return;
    refuse(e.hash ? `@${e.name}{...} with one key: perl warns that it is better written $${e.name}{...}`
        : `@${e.name}[...] with one index: perl warns that it is better written $${e.name}[...]`, e.pos);
};

// A `die` that is tested, or the left operand of an operator: perl warns
// `Possible precedence issue with control flow operator` of most of them,
// and none means anything (T303, D146). Through brackets and a unary plus.
const isDie = (e: Expr): boolean => {
    const p = plain(e);
    return p.kind === 'listop' && p.op === 'die';
};
const notTested = (e: Expr): void => {
    if (isDie(e)) refuse('a die that is tested: perl warns of a precedence problem, and a die is never worth anything', plain(e).pos);
};

// Everything that is checked of an expression wherever it stands.
// `my`: whether a `my` may stand here (D56, D21): at the head of a
// statement, or in the test of an `if`, and in neither under an operand
// that may not be worked out.
// `ctx`: where it stands. `root`: it is a statement's own expression, where
// an assignment of a list or to an array may stand (D78).
const checkExpr = (w: World, e: Expr, my: boolean, ctx: Ctx = 'scalar', root = false): void => {
    checkLiteral(e);
    if (e.kind === 'binary' && isDie(e.left)) refuse(`a die on the left of '${e.op}': perl warns of a precedence problem, and a die is never worth anything`, plain(e.left).pos);
    if (e.kind === 'ternary') notTested(e.test);
    checkConcat(w, e);
    if (ctx === 'scalar') checkOneValue(w, e);
    if ((e.kind === 'my' || e.kind === 'myarray' || (e.kind === 'list' && e.my)) && !my) {
        refuse(`${e.kind === 'my' ? `my $${e.name}` : e.kind === 'myarray' ? `my ${e.hash ? '%' : '@'}${e.name}` : 'my (...)'} here: a my begins a statement or a for, or stands in the test of an if or a while, where it is always reached`, e.pos);
    }
    if ((e.kind === 'listassign' || (e.kind === 'assign' && (e.target.kind === 'array' || e.target.kind === 'myarray' || e.target.kind === 'deref'))) && !root) {
        refuse('an assignment of a list is a statement: perl gives the count of its right side as its value (D78)', e.pos);
    }
    // A list that is only declarations is a statement's; anywhere else a
    // `my` in a list is a list assignment's left side, which the parser
    // has made of it.
    if (e.kind === 'list' && e.my) return;
    checkSliceOfOne(e);
    if (e.kind === 'hashop' && e.keys !== undefined) {
        if (e.deref === undefined) checkSliceOfOne({ kind: 'slice', name: e.name, hash: true, indexes: e.keys, pos: e.at });
        checkOrder(w, 'delete', [...e.keys, ...(e.deref !== undefined ? [e.deref] : [])], true);
    }
    // perl warns as it compiles of an index written as a string that is
    // no number, `$a["x"]`: `Argument "x" isn't numeric`. The shapes are
    // D40's, which the runtime has for a string met as the program runs.
    if ((e.kind === 'elem' || e.kind === 'chain') && !e.hash) {
        const index = plain(e.index);
        if (index.kind === 'str' && !NUMERIC_STRING.test(index.value)) {
            refuse(`${index.text} as an index is not a number: perl warns of it as it compiles`, index.pos);
        }
    }
    const of = e.kind === 'apply' ? plain(e.args[0]!) : undefined;
    // (And of the whole container through a reference, T256.)
    if (e.kind === 'apply' && (e.name === 'length' || e.name === 'defined') && (of?.kind === 'array' || (of?.kind === 'deref' && !of.last))) {
        refuse(`${e.name} of ${of.hash ? 'a hash' : 'an array'}: perl ${e.name === 'length' ? 'warns, and means the length of its count' : 'refuses it'}; scalar(${of.hash ? '%h' : '@a'}) is how many it holds`, e.pos);
    }
    if (e.kind === 'chain') checkHops(w, e);
    // D247: perl 5.42 folds away a list repeated by the integer 1 as it
    // compiles, and where a `? :` or a logical operator may jump past it
    // the program goes on at the wrong op: garbage, or out of memory
    // (T603). So there a list's count may not be 1, nor what perl works
    // out as it compiles, which this does not: a number written out,
    // other than the integer 1, or a string, is the count.
    if (e.kind === 'ternary') { checkPassedRepeat(e.then); checkPassedRepeat(e.else); }
    if (e.kind === 'binary' && infixOp(e.op)?.when) checkPassedRepeat(e.right);
    // D76, for what this node works out in order.
    if (e.kind === 'binary' && !infixOp(e.op)?.when) checkOrder(w, `'${e.op}'`, [e.left, e.right], ctx === 'list' && isRepeat(e));
    if (e.kind === 'apply') checkOrder(w, e.name, e.args, false);
    if (e.kind === 'list') checkOrder(w, 'this list', e.items, true);
    if (e.kind === 'slice') checkOrder(w, 'this slice', [...e.indexes, ...(e.items ?? []), ...(e.deref !== undefined ? [e.deref] : [])], true);
    // (Through a reference the container comes first: step 13b.)
    if (e.kind === 'arrayop') checkOrder(w, e.op, [...(e.deref !== undefined ? [e.deref] : []), ...e.args], true);
    // `join`'s separator is read when `join` runs, so it is the first
    // item of its list (T186, D87).
    if (e.kind === 'listop' && e.op === 'sprintf') checkFormat(e.args, 'sprintf', e.pos);
    if (e.kind === 'listop') checkOrder(w, e.op, e.args, true);
    if (e.kind === 'sort' && e.body === undefined) {
        checkOrder(w, "sort's list", e.items, true);
        e.items.forEach(x => checkExpr(w, x, false, 'list'));
    }
    if (e.kind === 'sort' && e.body !== undefined) {
        bound(w, "sort's list", 'the sort', e.items, e.body);
        const last = e.body.at(-1);
        if (last?.kind !== 'do') throw new Error('a sort block with no value');
        e.body.slice(0, -1).forEach(s => checkStmt(w, s));
        // One value, which says which of the two comes first.
        checkExpr(w, last.expr, true, 'scalar');
    }
    if (e.kind === 'binder') {
        bound(w, `${e.op}'s list`, `the ${e.op}`, e.items, e.body);
        const last = e.body.at(-1);
        if (last === undefined) throw new Error(`a ${e.op} block with no value`);
        e.body.slice(0, -1).forEach(s => checkStmt(w, s));
        // A block that ends in a `say` is worth `true` (D70).
        if (last.kind !== 'do') return checkStmt(w, last);
        // `map`'s block gives a list, and `grep`'s one value, which is
        // tested (D53).
        if (e.op === 'grep') tested(last.expr);
        checkExpr(w, last.expr, true, e.op === 'grep' ? 'scalar' : 'list');
    }
    if (e.kind === 'invoke') {
        // The arguments are copied into a list when one of them is a
        // list; otherwise a scalar variable is handed over as a place, and
        // read late, as perl reads it (D73).
        checkOrder(w, `the arguments of ${e.name}`, e.args, e.args.some(a => listy(a) || handsOn(a, gives(w))), { changes: calleeDefaults(w, e), at: e });
    }
    // Step 14: through a reference the same, what stands before the arrow
    // the last part (T370, D166), and the defaults of any sub a reference
    // can be to after them all (D163).
    if (e.kind === 'callref') {
        checkOrder(w, 'a call through a reference', [...e.args, e.head], e.args.some(a => listy(a) || handsOn(a, gives(w))), { changes: calleeDefaults(w, e), at: e });
    }
    // Step 17a: the invocant is the first part (T429), and the methods'
    // defaults run after them all; `new`'s arguments are places, read at
    // their fields' turns, after the defaults above them (T427, D178).
    if (e.kind === 'methcall') {
        checkOrder(w, `the call of the method ${e.name}`, [e.invocant, ...e.args], e.args.some(a => listy(a) || handsOn(a, gives(w))), { changes: calleeDefaults(w, e), at: e });
    }
    if (e.kind === 'new') {
        checkOrder(w, `the arguments of ${e.cls ?? '__CLASS__'}->new`, e.args, e.args.some(a => listy(a) || handsOn(a, gives(w))), { changes: calleeDefaults(w, e), at: e });
    }
    if (e.kind === 'anonsub') checkSub(w, e.sub);
    // The scalar through a reference (step 13c) is stored to as an element
    // through one is, its head's parts for the index.
    if (e.kind === 'assign' && (e.target.kind === 'elem' || e.target.kind === 'chain' || e.target.kind === 'sderef')) {
        // `=`: the right side, then the index. The others: the index,
        // the target made, then the right side, which may not change the
        // array the target is in (T158, T159).
        // Through a reference (step 13a), the chain left to right for the
        // index, its hops made as it goes; making one may change what the
        // right side is (T249).
        const index = e.target.kind === 'chain' ? chainParts(e.target) : e.target.kind === 'sderef' ? derefParts(e.target) : [e.target.index];
        if (infixOp(e.op)?.rt === undefined && infixOp(e.op)?.when === undefined) {
            checkOrder(w, `'${e.op}'`, [e.value, ...index], false);
            if (e.target.kind === 'chain' || e.target.kind === 'sderef') checkMaking(w, e.target, e.value, false);
            // perl makes one operation of a concatenation and the store
            // of it, and joins the pieces after the index is worked out:
            // `$a[$i = 2] = $i . "v"` stores `2v` (T230). An interpolated
            // string of more than one piece is such a row. So the index
            // may not change a variable the row reads, itself or through
            // a sub it calls; through whatever gives one operand or the
            // other, which perl may have folded away.
            const row = wholes(e.value).filter(v => (v.kind === 'binary' && infixOp(v.op)?.concat === true) || (v.kind === 'interp' && v.parts.length > 1));
            const names = new Set<string>();
            const ids = new Set<number>();
            for (const r of row) {
                reads(r, names);
                (r.kind === 'interp' ? r.parts : [r]).forEach(x => variables(x).forEach(v => (v.kind === 'chain' || v.kind === 'sderef' ? ids.add(REACH) : addId(w, ids, w.names.of.get(v)!))));
                if (r.kind === 'interp') r.parts.forEach(x => reads(x, names));
            }
            const changed = index.flatMap(x => [...changes(x)]).find(name => names.has(name));
            const through = index.flatMap(x => [...changeSet(w, x)]).find(id => ids.has(id));
            if (changed !== undefined || through !== undefined) {
                const at = index.find(x => changes(x).has(changed ?? '') || changeSet(w, x).has(through ?? NaN)) ?? e.target;
                const what = e.target.kind === 'sderef' ? 'reference' : e.target.hash ? 'key' : 'index';
                refuse(`the ${what} changes ${changed !== undefined ? '$' + changed : sigil(w, through!)}, which the concatenation on the right reads: perl joins its pieces as it stores, after the ${what} is worked out; take the string into a my first`, at.pos);
            }
        }
        else checkOrder(w, `'${e.op}'`, [e.target, e.value], false);
    }
    // The whole container through a reference (step 13b): the right side,
    // then the head, the container made as it goes (T248, T249).
    if (e.kind === 'assign' && e.target.kind === 'deref') {
        checkOrder(w, `'${e.op}'`, [e.value, ...derefParts(e.target)], true);
        checkMaking(w, e.target, e.value, true);
    }
    if (e.kind === 'listassign') {
        // The right side, then every target's index, then the stores.
        // A target through a reference has its chain for its index, and
        // its hops are made then (step 13a; T249).
        // A slice or the whole container through a reference has its
        // head's parts after its indexes, and is made then (step 13b).
        const indexes = e.targets.flatMap(t => (t.kind === 'elem' ? [t.index] : t.kind === 'slice' ? [...t.indexes, ...(t.deref !== undefined ? derefParts(t.deref) : [])]
            : t.kind === 'chain' ? chainParts(t) : t.kind === 'deref' || t.kind === 'sderef' ? derefParts(t) : []));
        checkOrder(w, 'this assignment', [e.value, ...indexes], true);
        e.targets.forEach(t => {
            if (t.kind === 'chain' || t.kind === 'deref' || t.kind === 'sderef') checkMaking(w, t, e.value, true);
            if (t.kind === 'slice' && t.deref !== undefined) checkMaking(w, t.deref, e.value, true);
        });
        e.targets.forEach((t, n) => {
            const array = t.kind === 'array' || t.kind === 'myarray' || (t.kind === 'deref' && !t.last);
            // A slice is the one target of its assignment (D100): beside
            // others perl takes it, and it waits to be asked for.
            if (t.kind === 'slice' && t.name !== undefined && e.targets.length === 1 && !e.my) {
                checkSliceOfOne(t);
                return;
            }
            if (t.bracketed || !(t.kind === 'var' || t.kind === 'my' || t.kind === 'elem' || t.kind === 'chain' || t.kind === 'sderef' || array || (t.kind === 'constant' && t.name === 'undef'))) {
                refuse('a target of a list assignment is a variable, an element, undef, or, last, an array or a hash', t.pos);
            }
            if (array && n !== e.targets.length - 1) refuse(`${t.hash ? 'a hash' : 'an array'} among the targets takes every value that is left: it is the last target`, t.pos);
        });
    }
    if (e.kind === 'ternary') tested(e.test);
    if (e.kind === 'binary' && infixOp(e.op)?.when) tested(e.left);
    for (const [part, where] of children(e, ctx)) {
        // A `my` may stand in an operand that is always worked out.
        const reached = e.kind === 'ternary' ? part === e.test
            : e.kind === 'binary' && infixOp(e.op)?.when ? part === e.left
            : e.kind === 'assign' && infixOp(e.op)?.when ? part === e.target
            : true;
        // A target of a list assignment is no value, and its `undef` no
        // operand.
        if (e.kind === 'listassign' && part !== e.value) {
            if (part.kind === 'elem') checkExpr(w, part.index, false);
            if (part.kind === 'chain' || part.kind === 'sderef') checkExpr(w, part, false);
            if (part.kind === 'slice') part.indexes.forEach(x => checkExpr(w, x, false, 'list'));
            if (part.kind === 'slice' && part.deref !== undefined) checkExpr(w, part.deref.head, false);
            if (part.kind === 'deref') checkExpr(w, part.head, false);
            continue;
        }
        if (e.kind === 'assign' && part === e.target) {
            // (Where a `my` may stand is asked of a target too.)
            if (part.kind === 'elem') checkExpr(w, part.index, false);
            else if (part.kind === 'chain' || part.kind === 'sderef') checkExpr(w, part, false);
            else if (part.kind === 'deref') checkExpr(w, part.head, false);
            else if (part.kind === 'my' || part.kind === 'myarray') checkExpr(w, part, my && reached, 'list');
            continue;
        }
        checkExpr(w, part, my && reached, where);
    }
};

// `say`'s argument is in list context, and there perl's `x` repeats a
// list when its left operand is in brackets: `say(("a") x 3)` is three
// values, not one string. They print the same, and cost perl a value
// each, so a count the string would bear stops perl for lack of memory
// (T101). Lists are step 9's: until then the brackets are refused.
//
// The list reaches down: to the right operand of an operator that gives
// one operand or the other (`||`, `&&`, `//`, `or`, `and`), and to both
// branches of `? :` (T104). Not to a left operand, a condition, or
// through anything that makes one value of its operands.
//
// An argument of a call, the value of a `return` and a sub's last
// statement are lists to perl too, and there a call can count: `g(("a") x
// 0)` hands `g` no argument at all (T143, D73).
const checkListContext = (arg: Expr, where: string): void => {
    const visit = (in_: Expr): void => {
        const e = plain(in_);
        if (e.kind === 'ternary') {
            visit(e.then);
            visit(e.else);
        } else if (e.kind === 'binary' && infixOp(e.op)?.when) {
            visit(e.right);
        } else if (e.kind === 'binary' && infixOp(e.op)?.list && plain(e.left).bracketed) {
            refuse(`(...) ${e.op} ${where} repeats a list, to perl: take the brackets off the left operand`, e.pos);
        }
    };
    visit(arg);
};

// A pragma as it is said: `use utf8`, `no warnings`.
const said = (pragma: string): string => (pragma.startsWith('no ') ? pragma : `use ${pragma}`);

// A pragma is written one way (D16): its arguments are the table's, each
// a string literal. perl takes `use open qw(:std :encoding(UTF-8))` and
// `use open ':std', ':utf8'` too, and each is another thing to read.
const checkPragma = (p: Pragma): void => {
    const wanted = PRAGMAS.get(p.name)!.args;
    const written = p.args.map(a => (a.kind === 'str' && !a.bracketed ? a.value : undefined));
    if (written.length !== wanted.length || written.some((w, n) => w !== wanted[n])) {
        refuse(`'${said(p.name)}' is written: ${[said(p.name), wanted.map(a => `'${a}'`).join(', ')].join(' ').trim()};`, p.pos);
    }
};

// One of the expressions of the first part of a `for`, or of its third:
// what could be a statement, and a `my` in the first part only (D60).
const checkPart = (w: World, e: Expr, first: boolean): void => {
    // A call is something done, as it is where it is a statement (D72).
    if (e.kind !== 'assign' && e.kind !== 'step' && e.kind !== 'my' && !isCall(e) && !(e.kind === 'arrayop' && e.op !== 'scalar' && e.op !== 'splice') && !(e.kind === 'hashop' && e.op === 'delete')) {
        refuse('this part of the for only has a value, and nothing is done with it: perl warns that it is useless', e.pos);
    }
    const my = e.kind === 'my' ? e : e.kind === 'assign' && e.target.kind === 'my' ? e.target : undefined;
    if (e.kind === 'assign' && (e.target.kind === 'array' || e.target.kind === 'myarray' || e.target.kind === 'deref')) refuse('an array is assigned in a statement of its own, not in a part of a for', e.pos);
    if (my === undefined) return checkExpr(w, e, false);
    if (!first) refuse(`my $${my.name} in the third part of a for: a my is in the first part, and is one variable for the whole loop`, my.pos);
    if (e.kind !== 'assign') return;
    checkConcat(w, e);
    checkExpr(w, e.value, false);
};

// The list of a `foreach`, a `map` or a `grep`, and what its block may
// not do to it (D76, D77). perl walks the variables themselves (T13,
// T180), and here the list is a copy: so nothing the block does may change
// a scalar its list names, anywhere in it (T162). An array it names is
// frozen as the program runs.
const bound = (w: World, what: string, binder: string, items: readonly Expr[], body: readonly Stmt[], lone = false): void => {
    checkOrder(w, what, items, true);
    items.forEach(e => checkExpr(w, e, false, 'list'));
    const scalars = new Map<number, Expr>();
    // A scalar variable whose reference is taken, and the scalar through a
    // reference, are what references reach too (step 13c; D109): perl's
    // loop walks the scalar itself, whoever stores to it (T347).
    const collect = (e: Expr): void => {
        if (e.kind === 'var') scalars.set(w.names.of.get(e)!, e);
        if (e.kind === 'var' && w.names.taken.has(w.names.of.get(e)!)) scalars.set(CELLS, e);
        if (e.kind === 'sderef') scalars.set(CELLS, e);
        parts(e).forEach(collect);
    };
    items.forEach(collect);
    const refused = (id: number, at: Expr): never =>
        refuse(`this can change ${sigil(w, id)}, which the list of ${binder} it is in names: perl's ${binder.replace('the ', '')} walks the variable itself; take the value into a my before ${binder}`, at.pos);
    const guard = (e: Expr): void => {
        for (const id of changesItself(w, e)) {
            if (scalars.has(id)) refused(id, e);
            if (scalars.has(CELLS) && w.names.taken.has(id) && !w.names.isArray[id]) refused(CELLS, e);
        }
        if (isCall(e)) for (const id of calleeChanges(w, e)) if (scalars.has(id)) refused(id, e);
        parts(e).forEach(guard);
    };
    // A loop's lone range has its ends worked out once, before the loop
    // (step 16d, D259; T172): nothing the block stores to changes it.
    if (scalars.size > 0 && !lone) body.forEach(b => expressions(b, guard));
};

// A statement below the top of the file. `modified`: it stands before an
// `if` or `unless` modifier, where a `my` may be skipped and leave the
// last value behind (T30).
const checkStmt = (w: World, s: Stmt, modified = false, last = false): void => {
    switch (s.kind) {
    case 'use': return refuse(`'use ${s.version};' here: the version is the first statement, and is said once`, s.pos);
    case 'pragma': return refuse(`'${said(s.name)}' goes at the top, after 'use ${VERSION};' and before anything else`, s.pos);
    case 'call':
        if (s.name === 'printf') checkFormat(s.args, 'printf', s.pos);
        checkOrder(w, `${s.name}'s list`, s.args, true);
        return s.args.forEach(a => checkExpr(w, a, false, 'list'));
    case 'do':
        // perl warns of a statement that only has a value: `Useless use
        // of ... in void context` (T114).
        // A call is a statement. And a value alone is one where it is
        // the last of a sub, with no modifier: it is the sub's value
        // (D72, T140), a list to perl (T143).
        const does = s.expr.kind === 'assign' || s.expr.kind === 'step' || s.expr.kind === 'my' || isCall(s.expr)
            || s.expr.kind === 'myarray' || s.expr.kind === 'listassign' || (s.expr.kind === 'list' && s.expr.my === true)
            || (s.expr.kind === 'arrayop' && s.expr.op !== 'scalar')
            || (s.expr.kind === 'hashop' && s.expr.op === 'delete')
            // A `map` or a `grep` may be one, for what its block does: perl
            // does not warn of it (D87).
            || s.expr.kind === 'binder'
            // `die` and `warn` are done for what they do (step 15).
            || (s.expr.kind === 'listop' && (s.expr.op === 'die' || s.expr.op === 'warn'));
        // (perl is silent about `exists $h{k};` and `keys %h;`, which
        // sets `each`'s place back: nothing, here.)
        if (!does && !last && s.expr.kind === 'hashop') refuse('this statement only has a value, and nothing is done with it', s.pos);
        if (!does && !last) {
            refuse('this statement only has a value, and nothing is done with it: perl warns that it is useless', s.pos);
        }
        // The `my` a statement begins with is the one that may stand in it.
        const head = s.expr.kind === 'assign' ? s.expr.target : s.expr;
        const declares = head.kind === 'my' || head.kind === 'myarray' || (head.kind === 'list' && head.my === true) || (s.expr.kind === 'listassign' && s.expr.my === true);
        if (declares && modified) {
            refuse('my under a modifier: when the test fails, perl leaves in the variable what it last held; declare it in a statement of its own', head.pos);
        }
        // The `my` a statement begins with is the one that may stand in
        // it: its own, and no other.
        if (s.expr.kind === 'my' || s.expr.kind === 'myarray' || (s.expr.kind === 'list' && s.expr.my)) return;
        if (s.expr.kind === 'assign' && (head.kind === 'my' || head.kind === 'myarray')) {
            checkConcat(w, s.expr);
            return checkExpr(w, s.expr.value, false, head.kind === 'myarray' ? 'list' : 'scalar');
        }
        if (s.expr.kind === 'listassign') {
            // (Its targets are declarations, or checked as targets.)
            return checkExpr(w, s.expr, false, 'list', true);
        }
        return checkExpr(w, s.expr, false, 'list', true);
    case 'block': return s.body.forEach(b => checkStmt(w, b));
    case 'if':
        for (const arm of s.arms) {
            notTested(arm.test);
            tested(arm.test);
            checkExpr(w, arm.test, !s.modifier || s.joined === true);
            arm.body.forEach(b => checkStmt(w, b, s.modifier === true));
        }
        return s.otherwise?.forEach(b => checkStmt(w, b));
    // A loop's test is a test as an `if`'s is (D53, D62), and a `my` under
    // a `while` modifier is as one under `if` (T119).
    case 'while':
        notTested(s.test);
        tested(s.test);
        checkExpr(w, s.test, !s.modifier);
        return s.body.forEach(b => checkStmt(w, b, s.modifier === true));
    case 'for':
        s.first.forEach(e => checkPart(w, e, true));
        if (s.test) {
            notTested(s.test);
            tested(s.test);
            checkExpr(w, s.test, false);
        }
        s.each.forEach(e => checkPart(w, e, false));
        return s.body.forEach(b => checkStmt(w, b));
    // A loop over a list (D17, D77, D80).
    case 'foreach': {
        const lone = loneRange(s.items);
        bound(w, "the loop's list", 'the loop', s.items, s.body, lone);
        // A sub with no name that takes the loop's variable takes a copy,
        // and freezes for good what the loop froze (D162): so the list may
        // name no scalar variable, which is no container and has no freeze,
        // through any shape (T371, D166).
        const v = w.names.of.get(s.var)!;
        // Over a lone range the variable is a new number each time round,
        // never a scalar of the list's (D259; T669).
        if (w.names.captured.has(v) && !lone) {
            const scalar = s.items.flatMap(e => namesScalar(e)).at(0);
            if (scalar !== undefined) {
                refuse(`a sub with no name takes $${s.var.name}, the variable of a loop whose list names ${scalar}: to perl the sub has the scalar itself, and sees whatever is stored to it later (D166); take the value into a my in the block first, my $y = $${s.var.name};`, w.names.capturedAt.get(v)!);
            }
        }
        return s.body.forEach(b => checkStmt(w, b, s.modifier === true));
    }
    // Which loop it is for is the resolver's to say.
    case 'jump': return;
    // A `try`'s blocks are blocks (D143).
    case 'try':
        s.body.forEach(b => checkStmt(w, b));
        return s.handler.forEach(b => checkStmt(w, b));
    // A list, to a call that wants one (D18): the fault for a call that
    // wants one value is the runtime's.
    case 'return': return s.value === undefined ? undefined : checkExpr(w, s.value, false, 'list');
    // The parser lets a sub stand at the top level only, and a class.
    case 'sub': throw new Error('a sub below the top level');
    case 'class': throw new Error('a class below the top level');
    }
};

// The scalar variables an expression names anywhere, and the scalars it
// reads through a reference (step 14; T371): what a loop's list must not
// hold when a sub takes its variable.
const namesScalar = (e: Expr): string[] =>
    [...(e.kind === 'var' ? [`$${e.name}`] : e.kind === 'sderef' ? ['a scalar through a reference'] : []), ...parts(e).flatMap(namesScalar)];

// Every expression a statement holds, a test and a loop's list too, down
// through its blocks.
const expressions = (s: Stmt, f: (e: Expr) => void): void => {
    switch (s.kind) {
    case 'call': return s.args.forEach(f);
    case 'do': return f(s.expr);
    case 'return': return s.value === undefined ? undefined : f(s.value);
    case 'block': return s.body.forEach(b => expressions(b, f));
    case 'if':
        for (const arm of s.arms) {
            f(arm.test);
            arm.body.forEach(b => expressions(b, f));
        }
        return s.otherwise?.forEach(b => expressions(b, f));
    case 'while':
        f(s.test);
        return s.body.forEach(b => expressions(b, f));
    case 'for':
        [...s.first, ...(s.test ? [s.test] : []), ...s.each].forEach(f);
        return s.body.forEach(b => expressions(b, f));
    case 'foreach':
        s.items.forEach(f);
        return s.body.forEach(b => expressions(b, f));
    case 'sub': return s.body.forEach(b => expressions(b, f));
    case 'try':
        s.body.forEach(b => expressions(b, f));
        return s.handler.forEach(b => expressions(b, f));
    // Step 17a: the fields' defaults, and every sub of the class, its
    // parameters' defaults too.
    case 'class':
        s.init.body.forEach(b => expressions(b, f));
        return s.body.forEach(b => {
            if (b.kind !== 'sub') return;
            b.params.forEach(p => p.default && f(p.default));
            b.body.forEach(t => expressions(t, f));
        });
    default: return;
    }
};

// A `foreach`'s variable is read-only (D17): in perl it is the list's own
// element, and changing it changes the array.
const checkReadOnly = (program: Program, names: Resolution): void => {
    const variables = names.readonly;
    const w: World = { names, changed: [], defaults: [] };
    const guard = (e: Expr): void => {
        for (const id of changesItself(w, e, true)) {
            if (variables.has(id) && names.selfOf.includes(id)) refuse('$self is read-only (D175, T413): perl lets a method assign it, and the object is lost to the rest of the method', e.pos);
            if (variables.has(id)) refuse(['_', 'a', 'b'].includes(names.names[id]!) ? `$${names.names[id]} is read-only: in perl, changing it changes the list's own element; take the value into a my`
                : `$${names.names[id]} is its loop's variable, and read-only: in perl, changing it changes the list's own element; take the value into a my`, e.pos);
        }
        parts(e).forEach(guard);
    };
    program.body.forEach(s => expressions(s, guard));
    // And every sub with no name, its defaults too: a loop's variable it
    // takes is still the loop's (T372, D166).
    names.subs.filter(s => s.anon).forEach(s => {
        s.params.forEach(p => p.default && guard(p.default));
        s.body.forEach(b => expressions(b, guard));
    });
};

// A sub (D72): its parameters, and its body, whose last statement may be
// a value alone. (Its name is the parser's to refuse.)
const checkSub = (w: World, s: Sub): void => {
    let optional = false;
    for (const p of s.params) {
        if (p.op === undefined && !p.slurpy && optional) refuse('a required parameter after an optional one: perl refuses it', p.pos);
        optional = optional || p.op !== undefined;
        if (p.default) checkExpr(w, p.default, false);
    }
    s.body.forEach((b, n) => checkStmt(w, b, false, n === s.body.length - 1));
};

// A class (step 17a): each field's default, one value for a scalar's and
// a list for an array's or a hash's; and every sub of it, as a sub.
const checkClass = (w: World, c: Class): void => {
    for (const b of c.body) {
        if (b.kind === 'sub') {
            checkSub(w, b);
            continue;
        }
        if (b.default === undefined) continue;
        const scalar = b.var.kind === 'my';
        checkConcat(w, { kind: 'assign', op: '=', target: b.var, value: b.default, pos: b.pos });
        checkExpr(w, b.default, false, scalar ? 'scalar' : 'list');
    }
};

// The file variables each sub can change: its own assignments and steps,
// in its body and its defaults, and those of the subs it calls, and so on
// until nothing is added.
const changedBy = (names: Resolution): ReadonlySet<number>[] => {
    const own: Set<number>[] = [new Set()];
    const callees: Set<number>[] = [new Set()];
    const expr = (e: Expr, fn: number): void => {
        for (const id of changesItself({ names, changed: [], defaults: [] }, e)) {
            // What references reach is everyone's (D109). And what is not
            // the sub's own: a file variable, or for a sub with no name what
            // it captured (step 14; D163).
            if (id === REACH || id === CELLS || names.owner[id] !== fn) own[fn]!.add(id);
            // (A store to a sub's own scalar is to one made since the call
            // began, which nothing before the call has read through: so it
            // changes nothing a reference reached before, step 13c. An
            // array keeps 13a's rule.)
            const own_ = names.owner[id] === fn && !names.isArray[id];
            if (names.taken.has(id) && !own_) own[fn]!.add(REACH);
            if (names.taken.has(id) && !names.isArray[id] && !own_) own[fn]!.add(CELLS);
        }
        if (e.kind === 'invoke') callees[fn]!.add(names.calls.get(e)!);
        if (e.kind === 'callref') names.targets.forEach(t => callees[fn]!.add(t));
        // A method call, of every method of its name; `new`, of its fields'
        // defaults and `ADJUST` blocks (D172, D178).
        if (e.kind === 'methcall' || e.kind === 'new') names.targetsOf.get(e)!.forEach(t => callees[fn]!.add(t));
        parts(e).forEach(p => expr(p, fn));
    };
    const stmt = (s: Stmt, fn: number): void => {
        switch (s.kind) {
        case 'call': return s.args.forEach(a => expr(a, fn));
        case 'do': return expr(s.expr, fn);
        case 'return': return s.value === undefined ? undefined : expr(s.value, fn);
        case 'block': return s.body.forEach(b => stmt(b, fn));
        case 'if':
            for (const arm of s.arms) {
                expr(arm.test, fn);
                arm.body.forEach(b => stmt(b, fn));
            }
            return s.otherwise?.forEach(b => stmt(b, fn));
        case 'while':
            expr(s.test, fn);
            return s.body.forEach(b => stmt(b, fn));
        case 'for':
            [...s.first, ...(s.test ? [s.test] : []), ...s.each].forEach(e => expr(e, fn));
            return s.body.forEach(b => stmt(b, fn));
        case 'foreach':
            s.items.forEach(e => expr(e, fn));
            return s.body.forEach(b => stmt(b, fn));
        case 'try':
            s.body.forEach(b => stmt(b, fn));
            return s.handler.forEach(b => stmt(b, fn));
        default: return;
        }
    };
    for (const [n, s] of names.subs.entries()) {
        own.push(new Set());
        callees.push(new Set());
        s.params.forEach(p => p.default && expr(p.default, n + 1));
        s.body.forEach(b => stmt(b, n + 1));
    }
    for (let grew = true; grew;) {
        grew = false;
        for (const [fn, set] of own.entries()) {
            for (const callee of callees[fn]!) {
                for (const id of own[callee]!) {
                    if (!set.has(id)) {
                        set.add(id);
                        grew = true;
                    }
                }
            }
        }
    }
    return own;
};

export const check = (program: Program, names: Resolution): void => {
    const changed = changedBy(names);
    // What a sub's defaults can change, by themselves and through the
    // subs they call: file variables and arrays.
    const partial: World = { names, changed, defaults: [] };
    const defaults = [new Set<number>(), ...names.subs.map((sub, n) => {
        const set = new Set<number>();
        for (const p of sub.params) {
            if (p.default) for (const id of changeSet(partial, p.default)) if (id === REACH || id === CELLS || names.owner[id] !== n + 1) set.add(id);
        }
        return set;
    })];
    const w: World = { names, changed, defaults };
    checkReadOnly(program, names);
    // The line that makes the file mean the same thing to perl (D16).
    const first = program.body[0];
    if (first === undefined || first.kind !== 'use' || first.version !== VERSION) {
        refuse(`a program begins 'use ${VERSION};'`, first?.pos ?? program.end);
    }
    // The pragmas come next, each once at most, before anything else.
    const seen = new Set<string>();
    let pragmas = true;
    for (const stmt of program.body.slice(1)) {
        if (stmt.kind === 'pragma' && pragmas) {
            if (seen.has(stmt.name)) refuse(`'${said(stmt.name)}' is said once`, stmt.pos);
            seen.add(stmt.name);
            checkPragma(stmt);
        } else if (stmt.kind === 'sub') {
            pragmas = false;
            checkSub(w, stmt);
        } else if (stmt.kind === 'class') {
            pragmas = false;
            // perl 5.42 compiles `class` under `use experimental 'class'`
            // alone (step 17a).
            if (!seen.has('experimental')) refuse(`class needs use experimental 'class'; at the top, with the pragmas: perl 5.42 does not compile it without`, stmt.pos);
            checkClass(w, stmt);
        } else {
            pragmas = false;
            checkStmt(w, stmt);
        }
    }
};
