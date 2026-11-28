// What an expression is by how it is written, where more than one pass
// has to agree on it (D18): whether a `return`'s value is list-shaped, and
// which subs give a list back.
import { infixOp, prefixOp } from './names.ts';
import type { CallRef, Expr, Invoke, MethCall, New, Stmt, Sub } from './ast.ts';

// An expression behind any unary plus, which hands on where it stands.
export const behind = (e: Expr): Expr => (e.kind === 'unary' && prefixOp(e.op)?.rt === undefined ? behind(e.operand) : e);

const isRange = (e: Expr): boolean => e.kind === 'binary' && infixOp(e.op)?.range === true;
const isRepeat = (e: Expr): boolean => e.kind === 'binary' && infixOp(e.op)?.list === true && (e.left.kind === 'list' || e.left.bracketed === true);

// Whether a call is of a sub that gives a list back. A call through a
// reference is of any sub a reference can be to (step 14; D163).
// (And a method call, of any method of its name, D172; `new` gives one
// value, step 17a.)
export type Call = Invoke | CallRef | MethCall | New;
export type Gives = (call: Call) => boolean;
export const isCall = (e: Expr): e is Call => e.kind === 'invoke' || e.kind === 'callref' || e.kind === 'methcall' || e.kind === 'new';

// A call whose values a place hands on as they come: the call itself,
// through a unary plus, a branch of `? :`, or the right of `|| && //`.
export const handsOn = (in_: Expr, gives: Gives): boolean => {
    const e = behind(in_);
    return (isCall(e) && gives(e))
        || (e.kind === 'ternary' && (handsOn(e.then, gives) || handsOn(e.else, gives)))
        || (e.kind === 'binary' && infixOp(e.op)?.when !== undefined && handsOn(e.right, gives));
};

// List-shaped (D18): what gives a call for one value something other
// than its one value, in perl (T183). An array, a list of two or more, or
// of one that is itself list-shaped, a range, a slice, `(LIST) x N`,
// `splice`, `reverse`, `map`, `grep`, `sort`, and `? :` or `|| && //` with such an arm, whichever
// arm is taken; a hash, and `keys` and `values` (T229). `(LIST)[N]` with one index that is one value is that
// element; `()` is nothing, as `return;` is.
export const shaped = (in_: Expr, gives: Gives): boolean => {
    const e = behind(in_);
    switch (e.kind) {
    case 'array': return true;
    // The whole container through a reference (step 13b), as `@a` and `%h`.
    case 'deref': return e.last !== true;
    case 'list': return e.items.length > 1 || (e.items.length === 1 && shaped(e.items[0]!, gives));
    case 'slice': return e.name !== undefined || e.indexes.length !== 1 || shaped(e.indexes[0]!, gives) || handsOn(e.indexes[0]!, gives);
    case 'arrayop': return e.op === 'splice';
    case 'listop': return e.op === 'reverse';
    case 'hashop': return e.op === 'keys' || e.op === 'values' || e.keys !== undefined;
    case 'binder': return true;
    case 'sort': return true;
    case 'ternary': return shaped(e.then, gives) || shaped(e.else, gives);
    case 'binary': return isRange(e) || isRepeat(e) || (infixOp(e.op)?.when !== undefined && shaped(e.right, gives));
    default: return false;
    }
};

// Where a call that wants nothing hands that on, in what a sub gives back
// (D245): behind a unary plus, to each item of a list, to both branches of
// `? :` and to the right of `|| && //`. perl works out what stands there
// for nothing, which is not what it does for a list: a range is a
// flip-flop, `(LIST) x N` and `reverse` work for one value, a sort is
// skipped, its list worked out and its block never run, and a call is
// for nothing too (T600, T601; codegen's genVoid).
const voidReach = (in_: Expr, found: (e: Expr) => boolean): boolean => {
    const e = behind(in_);
    if (found(e)) return true;
    switch (e.kind) {
    case 'list': return e.items.some(item => voidReach(item, found));
    case 'ternary': return voidReach(e.then, found) || voidReach(e.else, found);
    case 'binary': return infixOp(e.op)?.when !== undefined && voidReach(e.right, found);
    default: return false;
    }
};

// A range, `(LIST) x N` or `reverse` where a call for nothing reaches it:
// a fault, as the call begins to give it back (D245).
export const voidOneValue = (e: Expr): boolean =>
    voidReach(e, x => isRange(x) || isRepeat(x) || (x.kind === 'listop' && x.op === 'reverse'));

// What a sub may give back: the value of each `return` in it, and its last
// statement if that is an expression.
const returned = (s: Sub): Expr[] => {
    const found: Expr[] = [];
    const walk = (t: Stmt): void => {
        switch (t.kind) {
        case 'return':
            if (t.value) found.push(t.value);
            return;
        case 'block': case 'while': case 'for': case 'foreach': return t.body.forEach(walk);
        case 'try':
            t.body.forEach(walk);
            return t.handler.forEach(walk);
        case 'if':
            t.arms.forEach(arm => arm.body.forEach(walk));
            return t.otherwise?.forEach(walk);
        default: return;
        }
    };
    s.body.forEach(walk);
    const last = s.body.at(-1);
    if (last?.kind === 'do') found.push(last.expr);
    return found;
};

// Which subs give a list back, by number, the file being 0: one with a
// list-shaped `return` or last statement, or one that hands on the values
// of a call of such a sub; and so on until nothing is added.
// (And a call through a reference hands on the values of any of `targets`
// that gives a list: step 14, D163.)
export const listSubs = (subs: readonly Sub[], calls: ReadonlyMap<Invoke, number>, targets: readonly number[], targetsOf: ReadonlyMap<Expr, readonly number[]>): boolean[] => {
    const lists = [false, ...subs.map(() => false)];
    const gives: Gives = call => (call.kind === 'invoke' ? lists[calls.get(call)!] === true
        : call.kind === 'callref' ? targets.some(t => lists[t] === true)
        : call.kind === 'new' ? false
        : (targetsOf.get(call) ?? []).some(t => lists[t] === true));
    for (let grew = true; grew;) {
        grew = false;
        for (const [n, s] of subs.entries()) {
            if (!lists[n + 1] && returned(s).some(e => shaped(e, gives) || handsOn(e, gives))) {
                lists[n + 1] = true;
                grew = true;
            }
        }
    }
    return lists;
};
