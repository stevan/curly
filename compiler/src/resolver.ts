// Names to their declarations (D29): every `$x` is tied to the `my` it
// means before any code is made, and the three ways that can fail are
// refused here, as perl refuses or warns of each (D56):
//   a variable with no `my` in sight (perl: `Global symbol requires
//   explicit package name`);
//   a second `my` of a name in one scope (perl warns that it masks the
//   first);
//   `my $x = $x` with no outer `$x`, which is the first again: a `my` is
//   seen from the statement after its own (T58).
// A scope is a block, and an `if` with its tests: a `my` in a test is
// seen in the blocks of that `if`, in its later tests, and no further. A
// loop is one too, for its test or its first part.
//
// And each `last` and `next` to its loop (D59, D61, D62), refused when
// there is none: perl looks for the loop as the program runs, and dies
// there.
//
// And each call to its sub (D72), wherever in the file the sub is; one
// the program doesn't have is refused, where perl dies when it gets
// there. A sub is a function of its own: its parameters and its
// variables are its frame's, it may name the file's variables that were
// declared before it, and no `last` or `next` in it reaches a loop
// outside it (T60).
import { refuse } from './errors.ts';
import type { AnonSub, Binder, CallRef, Expr, Foreach, Sort, Invoke, Jump, Loop, My, MyArray, Pos, Program, Stmt, Sub, SubRef } from './ast.ts';
import { listSubs, loneRange } from './shapes.ts';

// A declaration is a number, in the order the `my`s are met; `of` says
// which one each variable in the tree means, and `names` what each is
// called. A loop is a number too: `loops` gives each its own, and `jumps`
// says which loop each `last` and `next` is for.
//
// `slots` says where each declaration's value is kept as the program runs
// (D66): the slot of its function's frame that is its depth among the
// variables in scope, so that the variables of a block that has ended
// leave their slots to the next one.
//
// A function is the file, 0, or a sub, numbered from 1 in the order they
// are written: `owner` says whose frame a declaration is in, `frames` how
// many slots each function's variables take at most, `subs` the subs, and
// `calls` which one each call is of. **A file variable**, a `my` at the
// top level, has a slot that nothing else is ever given, the first `file`
// slots of the file's frame: a sub may be called before the `my` runs, and
// what it put there is still there after (T134).
//
// An array is a declaration like any other, with a name of its own: `@x`
// and `$x` are two (D80). `isArray` says which a declaration is, and `of`
// has every node that names one: an array, an element, a slice, `$#x`, a
// builtin that takes one.
export type Resolution = {
    of: ReadonlyMap<Expr, number>;
    names: readonly string[];
    isArray: readonly boolean[];
    // A hash is a declaration as an array is, `%x` a third name beside
    // `@x` and `$x` (step 12): `isArray` is true of it, and `isHash` too.
    isHash: readonly boolean[];
    slots: readonly number[];
    owner: readonly number[];
    frames: readonly number[];
    file: number;
    fileIds: ReadonlySet<number>;
    subs: readonly Sub[];
    calls: ReadonlyMap<Invoke, number>;
    // Which functions give a list back (D18), by number.
    lists: readonly boolean[];
    loops: ReadonlyMap<Loop, number>;
    jumps: ReadonlyMap<Jump, number>;
    each: ReadonlyMap<Foreach | Binder | Sort, Each>;
    // The declarations that are a loop's variable or `$_`: read-only (D17).
    readonly: ReadonlySet<number>;
    // The arrays and hashes whose reference is taken anywhere in the
    // program, `\@a` or `\%h` (step 13a; D109): what a reference reaches
    // may be one of them, under any name.
    // And the scalar variables, `\$x` (step 13c): each lives in a cell,
    // its slot holding the cell and every use of it going through it.
    taken: ReadonlySet<number>;
    // Step 14. A sub with no name is a function too, numbered after the
    // named ones in the order met (`anonOf`); `parents` is the function each
    // is written in. `captures` is, for each function, the declarations of
    // another's it uses, in the order its reference holds them (D161): a
    // scalar among them lives in a cell, as a taken one does (`captured`).
    // A file variable is never captured: every function reaches it
    // through the context. `constants` gives the declaration whose slot, a
    // file variable's, holds the one value of a sub with no name that uses
    // nothing from outside it (D161), and of a named sub with a `\&name`.
    // `targets` is every function a call through a reference may be of
    // (D163). `capturedAt` is where each captured declaration is first used
    // in a sub that captures it; `loopVars` the variable of each `foreach`,
    // to what the loop holds.
    anonOf: ReadonlyMap<AnonSub, number>;
    parents: readonly number[];
    captures: readonly (readonly number[])[];
    captured: ReadonlySet<number>;
    constants: ReadonlyMap<number, number>;
    subrefs: ReadonlyMap<SubRef, number>;
    targets: readonly number[];
    capturedAt: ReadonlyMap<number, Pos>;
    loopVars: ReadonlyMap<number, Each>;
};

// What a `foreach` has beside its variable: `list`, a declaration no
// program can name, whose slot holds the loop's list while it runs; and
// `arrays`, every array named anywhere in the list, which the loop
// freezes (D80, T162).
// And `frozen`, when an element through a reference stands anywhere in
// the list (step 13a; D114, T251): another such declaration, whose slot
// holds every container the list went through, which the loop freezes too.
export type Each = { list: number; arrays: readonly number[]; frozen?: number };

// What is round a statement that perl counts as a loop: a loop, or a
// bare block, which runs once (T32).
// And the block of a `map` or a `grep`, which no `last` or `next` may leave
// (T59).
// And a sub with no name, which no `last` or `next` may leave (T365,
// D165): `anon`.
type Round = { loop: Loop } | { bare: Pos; post?: string } | { wall: string };

export const resolve = (program: Program): Resolution => {
    const of = new Map<Expr, number>();
    const names: string[] = [];
    const isArray: boolean[] = [];
    const isHash: boolean[] = [];
    // An array's name in a scope: with its sigil, so that it is its own.
    const key = (d: My | MyArray): string => (d.kind === 'myarray' ? (d.hash ? '%' : '@') : '') + d.name;
    // The hash a node names, looked up as it is met. `counted`: by `keys`,
    // which names nothing (T218): its list is copies.
    const hash = (e: Expr, name: string, counted = false): void => {
        // (A builtin's hash is at its own place, after the word.)
        const at = e.kind === 'hashop' ? e.at : e.pos;
        const found = [...scopes].reverse().find(scope => scope.has('%' + name));
        if (found === undefined) return refuse(`%${name} is not declared: my %${name}`, at);
        of.set(e, found.get('%' + name)!);
        seen(found.get('%' + name)!, at);
        // A hash named in the list of a loop, a map, a grep or a sort is
        // frozen while it runs, as an array is (D17, T217): not by its
        // `keys`, which are copies, and not in a string, which is one.
        if (!quoted && !counted) naming.forEach(set => set.add(found.get('%' + name)!));
    };
    // The array a node names, looked up as it is met.
    // A reference to it, `\@a`, names nothing (`counted`): the list it
    // stands in holds the reference, which no change to the array changes.
    const array = (e: Expr, name: string, counted = false): void => {
        if ((e.kind === 'array' || e.kind === 'elem' || e.kind === 'slice') && e.hash) return hash(e, name, counted);
        const found = [...scopes].reverse().find(scope => scope.has('@' + name));
        if (found === undefined) {
            // In a string, what was read may not be what was meant.
            const meant = !quoted ? '' : e.kind === 'elem'
                ? `; in a string $${name}[ is an element of @${name}: for the scalar and a bracket, \${${name}}[ or $${name}\\[`
                : '; in a string, \\@ is the character';
            return refuse(`@${name} is not declared: my @${name}${meant}`, e.pos);
        }
        of.set(e, found.get('@' + name)!);
        seen(found.get('@' + name)!, e.pos);
        // A string is a copy: an array in one is not named by the list
        // the string stands in (T209).
        if (!quoted && !counted) naming.forEach(set => set.add(found.get('@' + name)!));
    };
    // Whether what is being read is a piece of a string (step 11a).
    let quoted = false;
    // The arrays named while the list of a `foreach`, a `map` or a `grep`
    // is read: one set for each list that is being read.
    const naming: Set<number>[] = [];
    // And for each, whether an element through a reference stands in it.
    const chains: boolean[] = [];
    const taken = new Set<number>();
    const each = new Map<Foreach | Binder | Sort, Each>();
    const readonly = new Set<number>();
    // The most slots in use since the statement in hand began: a `map`
    // in it has slots of its own while it runs.
    let peak = 0;
    const slots: number[] = [];
    const owner: number[] = [];
    const frames: number[] = [0];
    // The function being read, and of its variables that share slots, how
    // many are in scope and how many there have been at once.
    let fn = 0;
    let inScope = 0;
    let variables = 0;
    let file = 0;
    const fileSlots = new Set<number>();
    const fileScope = new Map<string, number>();
    let scopes: Map<string, number>[] = [fileScope];
    const close = (): void => {
        inScope -= scopes.pop()!.size;
    };
    const loops = new Map<Loop, number>();
    const jumps = new Map<Jump, number>();
    let round: Round[] = [];

    // The subs, before anything is read: a call may come before its sub.
    // The subs with no name are added as they are met (step 14).
    const subs: Sub[] = program.body.filter(s => s.kind === 'sub');
    const anonOf = new Map<AnonSub, number>();
    const parents: number[] = [0, ...subs.map(() => 0)];
    const captures: number[][] = [[], ...subs.map(() => [])];
    const uses: boolean[] = [false, ...subs.map(() => false)];
    const isAnon: boolean[] = [false, ...subs.map(() => false)];
    const captured = new Set<number>();
    const capturedAt = new Map<number, Pos>();
    const subrefs = new Map<SubRef, number>();
    const referred = new Set<number>();
    const loopVars = new Map<number, Each>();
    // The functions the one being read is written in, the file first.
    let nest: number[] = [0];
    // The names `$_`, `$a` and `$b` that a sub with no name does not see,
    // and the declarations of the statements it stands in, not yet seen
    // (T362, T376).
    let hidden = new Set<string>();
    const pending: { fn: number; ds: (My | MyArray)[] }[] = [];
    const called = new Map<string, number>();
    for (const [n, s] of subs.entries()) {
        if (called.has(s.name)) refuse(`a second sub called ${s.name}: perl warns that it is redefined, and takes this one`, s.named);
        called.set(s.name, n + 1);
    }
    const calls = new Map<Invoke, number>();

    // A declaration comes into scope: a file variable in a slot of its
    // own, any other at its depth among those in scope.
    const declare = (d: My | MyArray): void => {
        const id = of.get(d)!;
        scopes.at(-1)!.set(key(d), id);
        owner[id] = fn;
        if (scopes.at(-1) === fileScope) {
            fileSlots.add(id);
            slots[id] = file;
            file += 1;
            return;
        }
        slots[id] = inScope;
        inScope += 1;
        variables = Math.max(variables, inScope);
        peak = Math.max(peak, inScope);
    };

    // A declaration used in the function being read (step 14): one of
    // another function's is used by every sub with no name between the two,
    // which captures it, unless it is a file variable (D161, T375).
    const seen = (id: number, at: Pos): void => {
        const o = owner[id]!;
        if (o === fn) return;
        for (const f of nest.slice(nest.lastIndexOf(o) + 1)) {
            if (!isAnon[f]) continue;
            uses[f] = true;
            if (fileSlots.has(id)) continue;
            if (!captures[f]!.includes(id)) captures[f]!.push(id);
            captured.add(id);
            if (!capturedAt.has(id)) capturedAt.set(id, at);
        }
    };

    // The variables an expression uses, each looked up as it is met; and
    // the ones it declares, which are returned and not yet seen.
    const walk = (e: Expr, declared: (My | MyArray)[]): void => {
        switch (e.kind) {
        case 'var': {
            const found = [...scopes].reverse().find(s => s.has(e.name));
            // (In a sub with no name: perl's are the globals, read when the
            // sub runs, T362.)
            if (found === undefined && hidden.has(e.name)) return refuse(`$${e.name} in a sub with no name: to perl it is the global $${e.name}, read when the sub runs, and not the ${e.name === '_' ? "for's, map's or grep's" : "sort's"} round it (D162); take the value into a my first`, e.pos);
            if (found === undefined && pending.some(q => q.fn !== fn && q.ds.some(d => d.kind === 'my' && d.name === e.name))) {
                return refuse(`$${e.name} is not declared yet: a my is seen from the statement after it (D55), and the sub is made before the store; write my $${e.name}; $${e.name} = sub { ... };, or __SUB__ for the sub itself`, e.pos);
            }
            if (found === undefined && (e.name === 'a' || e.name === 'b')) return refuse(`$${e.name} outside the block of a sort: $a and $b are the two values a sort gives its block, and are seen there alone`, e.pos);
            if (found === undefined && e.name === '_') return refuse('$_ outside the block of a for, a map or a grep: it is the value they give their block, and is seen there alone (D17)', e.pos);
            if (found === undefined) {
                return refuse(`$${e.name} is not declared: my $${e.name}${quoted ? '; in a string, \\$ is the character, and ${name} ends a name sooner' : ''}`, e.pos);
            }
            of.set(e, found.get(e.name)!);
            seen(found.get(e.name)!, e.pos);
            return;
        }
        // Step 14: a sub with no name, a function of its own read where it
        // stands; a call through a reference, its arguments first (T370);
        // `\&name`; `__SUB__`.
        case 'anonsub': {
            const n = subs.push(e.sub);
            anonOf.set(e, n);
            parents[n] = fn;
            captures[n] = [];
            uses[n] = false;
            isAnon[n] = true;
            pending.push({ fn, ds: declared });
            function_(e.sub, n);
            pending.pop();
            return;
        }
        case 'callref':
            e.args.forEach(a => walk(a, declared));
            return walk(e.head, declared);
        case 'subref': {
            const found = called.get(e.name);
            if (found === undefined) return refuse(`\\&${e.name}: the program has no sub called ${e.name}`, e.pos);
            subrefs.set(e, found);
            referred.add(found);
            return;
        }
        case 'cursub':
            if (!isAnon[fn]) return refuse("__SUB__ outside a sub with no name: perl gives undef at the top of the file and the sub itself in a named one; write the sub's name, or \\&name", e.pos);
            return;
        case 'interp': {
            const outer = quoted;
            quoted = true;
            e.parts.forEach(x => walk(x, declared));
            quoted = outer;
            return;
        }
        case 'my':
        case 'myarray':
            of.set(e, names.length);
            isArray.push(e.kind === 'myarray');
            isHash.push(e.kind === 'myarray' && e.hash === true);
            names.push(e.name);
            declared.push(e);
            return;
        case 'array':
        case 'lastindex':
            return array(e, e.name);
        case 'elem':
            walk(e.index, declared);
            return array(e, e.name);
        // Step 13a: an element through a reference, its head first; a new
        // container; a reference to a variable's.
        case 'chain':
            walk(e.head, declared);
            walk(e.index, declared);
            if (!quoted) chains.fill(true);
            return;
        case 'anon': return e.items.forEach(x => walk(x, declared));
        // Step 13b: the whole container through a reference, which a loop
        // over it freezes as it does an element's (T237, T251).
        case 'deref':
            walk(e.head, declared);
            if (!quoted) chains.fill(true);
            return;
        // Step 13c: the scalar through a reference, its head first. (What a
        // loop freezes on its way is its head's: an element of a named
        // container, or a chain, which says so itself. The cell is frozen
        // by nothing: D77 keeps the block from storing to it.)
        case 'sderef':
            return walk(e.head, declared);
        case 'ref': {
            if (e.of.kind === 'array') array(e.of, e.of.name, true);
            else walk(e.of, declared);
            const id = of.get(e.of)!;
            // `\$x` (step 13c; D110): a loop's variable, `$_`, `$a` and `$b`
            // are the list's own elements to perl, and a reference to one
            // reaches into the list (D17, T12).
            if (e.of.kind === 'var' && readonly.has(id)) {
                return refuse(['_', 'a', 'b'].includes(e.of.name) ? `\\$${e.of.name}: a reference to $${e.of.name} is cut (D110): to perl it is the list's own element; take the value into a my first`
                    : `\\$${e.of.name}: a reference to a loop's variable is cut (D110): to perl it is the list's own element; take the value into a my first`, e.pos);
            }
            taken.add(id);
            return;
        }
        case 'slice':
            // Its indexes are worked out first (T163).
            e.indexes.forEach(x => walk(x, declared));
            e.items?.forEach(x => walk(x, declared));
            if (e.deref !== undefined) return walk(e.deref, declared);
            return e.name === undefined ? undefined : array(e, e.name);
        case 'list': return e.items.forEach(x => walk(x, declared));
        case 'arrayop':
            if (e.deref !== undefined) walk(e.deref, declared);
            e.args.forEach(x => walk(x, declared));
            return e.deref === undefined ? array(e, e.name) : undefined;
        case 'hashop':
            if (e.chain !== undefined) return walk(e.chain, declared);
            if (e.key !== undefined) walk(e.key, declared);
            e.keys?.forEach(x => walk(x, declared));
            if (e.deref !== undefined) return walk(e.deref, declared);
            return hash(e, e.name, e.op === 'keys' || e.op === 'count');
        case 'listop': return e.args.forEach(x => walk(x, declared));
        case 'sort': {
            // As a `map`: the list where the sort stands, then the block,
            // with `$a` and `$b` its own.
            const arrays = new Set<number>();
            naming.push(arrays);
            chains.push(false);
            e.items.forEach(x => walk(x, declared));
            naming.pop();
            const chained = chains.pop()!;
            if (e.body === undefined) return;
            scopes.push(new Map());
            bind(e, [e.a!, e.b!], arrays, chained);
            round.push({ wall: 'sort' });
            inner(e.body);
            round.pop();
            close();
            return;
        }
        case 'binder': {
            // The list is read where the binder stands, so a `$_` in it is
            // the one outside; then the block, in a scope of its own.
            const arrays = new Set<number>();
            naming.push(arrays);
            chains.push(false);
            e.items.forEach(x => walk(x, declared));
            naming.pop();
            const chained = chains.pop()!;
            scopes.push(new Map());
            bind(e, [e.var], arrays, chained);
            round.push({ wall: e.op });
            inner(e.body);
            round.pop();
            close();
            return;
        }
        case 'listassign':
            walk(e.value, declared);
            return e.targets.forEach(x => walk(x, declared));
        case 'assign':
            // The right side first: it is worked out first, and in `my $x
            // = $x` its `$x` is the outer one. (A sub with no name there that
            // uses `$x` is told so, T376.)
            if (e.target.kind === 'my') pending.push({ fn, ds: [e.target] });
            walk(e.value, declared);
            if (e.target.kind === 'my') pending.pop();
            return walk(e.target, declared);
        case 'step': return walk(e.target, declared);
        case 'unary': return walk(e.operand, declared);
        case 'binary':
            walk(e.left, declared);
            return walk(e.right, declared);
        case 'ternary':
            walk(e.test, declared);
            walk(e.then, declared);
            return walk(e.else, declared);
        case 'apply': return e.args.forEach(a => walk(a, declared));
        case 'invoke': {
            e.args.forEach(a => walk(a, declared));
            const found = called.get(e.name);
            if (found === undefined) return refuse(`the program has no sub called ${e.name}`, e.pos);
            calls.set(e, found);
            return;
        }
        default: return;
        }
    };

    // An expression of a statement, or a test, or the expressions of one
    // part of a `for`: what it declares is seen once the whole of it has
    // been read.
    const whole = (...es: Expr[]): void => {
        const declared: (My | MyArray)[] = [];
        const before = peak;
        peak = inScope;
        es.forEach(e => walk(e, declared));
        // What this declares is stored to as the statement begins, and a
        // `map` in the statement had slots of its own while it was read:
        // so these come after them (the slots between are let go with
        // the scope).
        if (declared.length > 0 && scopes.at(-1) !== fileScope) {
            for (; inScope < peak; inScope += 1) scopes.at(-1)!.set(` ${inScope}`, -1);
        }
        peak = Math.max(before, peak);
        // In the order they are written: the second of two is the one at
        // fault.
        declared.sort((a, b) => a.pos.line - b.pos.line || a.pos.col - b.pos.col);
        for (const d of declared) {
            const scope = scopes.at(-1)!;
            if (scope.has(key(d))) refuse(`my ${d.kind === 'myarray' ? (d.hash ? '%' : '@') : '$'}${d.name} again in one scope: perl warns that it masks the first`, d.pos);
            declare(d);
        }
    };

    // What a `foreach`, a `map` or a `grep` has in its scope: its list,
    // a declaration no program can name (no name has a blank in it), and
    // its variable.
    const bind = (binder: Foreach | Binder | Sort, variables: readonly My[], arrays: ReadonlySet<number>, chained: boolean): void => {
        const list: MyArray = { kind: 'myarray', name: 'the list', pos: binder.pos };
        const frozen: MyArray = { kind: 'myarray', name: 'the frozen', pos: binder.pos };
        for (const d of [list, ...(chained ? [frozen] : []), ...variables]) {
            of.set(d, names.length);
            isArray.push(d.kind === 'myarray');
            isHash.push(false);
            names.push(d.name);
            declare(d);
        }
        variables.forEach(v => readonly.add(of.get(v)!));
        const held: Each = chained ? { list: of.get(list)!, arrays: [...arrays], frozen: of.get(frozen)! } : { list: of.get(list)!, arrays: [...arrays] };
        each.set(binder, held);
        if (binder.kind === 'foreach') loopVars.set(of.get(binder.var)!, held);
    };

    const inner = (body: readonly Stmt[]): void => {
        scopes.push(new Map());
        body.forEach(statement);
        close();
    };

    // A sub: a function of its own, which sees the file's variables as
    // far as they have been declared. A default is read before its own
    // parameter exists, so `sub f($x = $x)` means the file's `$x` (T138);
    // the body is in the parameters' scope, so a `my` of a parameter's
    // name there is a second one (T141).
    // A sub with no name (step 14), `number` its function's, sees what is in
    // scope where it is written, but `$_`, `$a` and `$b` (T362), and no
    // `last` or `next` leaves it (T365). What the statement round it is
    // reading (a loop's list, the slots in use) is put aside while it is
    // read.
    const function_ = (s: Sub, number?: number): void => {
        const outer = { fn, inScope, variables, scopes, round, peak, quoted, nest, hidden };
        const lists = naming.splice(0);
        const chained = chains.splice(0);
        fn = number ?? called.get(s.name)!;
        inScope = 0;
        variables = 0;
        peak = 0;
        quoted = false;
        if (number === undefined) {
            scopes = [fileScope, new Map()];
            round = [];
            nest = [0, fn];
        } else {
            hidden = new Set(hidden);
            scopes = [...scopes.map(scope => {
                const seen_ = new Map(scope);
                for (const name of ['_', 'a', 'b']) if (seen_.delete(name)) hidden.add(name);
                return seen_;
            }), new Map()];
            round = [{ wall: 'anon' }];
            nest = [...nest, fn];
        }
        for (const p of s.params) {
            if (p.default) whole(p.default);
            if (p.rest !== undefined) {
                of.set(p.rest, names.length);
                isArray.push(true);
                isHash.push(p.rest.hash === true);
                names.push(p.rest.name);
                declare(p.rest);
            }
            if (p.my === undefined) continue;
            if (scopes.at(-1)!.has(p.my.name)) refuse(`two parameters called $${p.my.name}: perl warns that the second masks the first`, p.my.pos);
            of.set(p.my, names.length);
            isArray.push(false);
            isHash.push(false);
            names.push(p.my.name);
            declare(p.my);
        }
        s.body.forEach(statement);
        frames[fn] = variables;
        ({ fn, inScope, variables, scopes, round, peak, quoted, nest, hidden } = outer);
        naming.push(...lists);
        chains.push(...chained);
    };

    // perl's `last` in a `map` block leaves the loop round the `map`, and
    // warns (T59).
    const walled = (word: string, op: string): string => (op === 'anon'
        ? `${word} out of a sub with no name: perl leaves the loop of whatever called the sub, and warns (D165); give back a value that says to, and test it in the loop`
        : `${word} out of the block of a ${op}: a loop says it`);

    const statement = (s: Stmt): void => {
        switch (s.kind) {
        case 'sub': return function_(s);
        case 'return': return s.value === undefined ? undefined : whole(s.value);
        case 'call': return s.args.forEach(a => whole(a));
        case 'do': return whole(s.expr);
        case 'block':
            round.push({ bare: s.pos });
            inner(s.body);
            round.pop();
            return;
        case 'while':
            loops.set(s, loops.size);
            // `do { } while` (D253): the block, which no `last` or `next`
            // is for, then the test, which does not see the block's `my`s.
            if (s.post) {
                const only = s.body[0];
                if (s.body.length !== 1 || only?.kind !== 'block') throw new Error('a do while with no block');
                round.push({ bare: only.pos, post: s.negate ? 'until' : 'while' });
                inner(only.body);
                round.pop();
                return whole(s.test);
            }
            // As under `if`: the statement is written before its test.
            if (s.modifier) {
                s.body.forEach(statement);
                return whole(s.test);
            }
            scopes.push(new Map());
            whole(s.test);
            round.push({ loop: s });
            inner(s.body);
            round.pop();
            close();
            return;
        case 'for':
            loops.set(s, loops.size);
            scopes.push(new Map());
            whole(...s.first);
            if (s.test) whole(s.test);
            whole(...s.each);
            round.push({ loop: s });
            inner(s.body);
            round.pop();
            close();
            return;
        case 'foreach': {
            loops.set(s, loops.size);
            // The list is read where the loop stands: the loop's variable
            // is not in it.
            const arrays = new Set<number>();
            naming.push(arrays);
            chains.push(false);
            whole(...s.items);
            naming.pop();
            const chained = chains.pop()!;
            scopes.push(new Map());
            // A lone range freezes nothing its ends name (step 16d, D259):
            // perl works them out once, before the loop (T668).
            const lone = loneRange(s.items);
            bind(s, [s.var], lone ? new Set() : arrays, lone ? false : chained);
            round.push({ loop: s });
            inner(s.body);
            round.pop();
            close();
            return;
        }
        case 'jump': {
            if (s.label !== undefined) {
                const name = s.label.name;
                const found = [...round].reverse().find(r => 'wall' in r || ('loop' in r && r.loop.label?.name === name));
                if (found !== undefined && 'wall' in found) return refuse(walled(s.name, found.wall), s.pos);
                if (found === undefined || !('loop' in found)) return refuse(`no loop called ${name} is round this ${s.name}`, s.label.pos);
                jumps.set(s, loops.get(found.loop)!);
                return;
            }
            const nearest = round.at(-1);
            if (nearest === undefined) return refuse(`${s.name} outside a loop`, s.pos);
            if ('wall' in nearest) return refuse(walled(s.name, nearest.wall), s.pos);
            // To perl a bare block is a loop that runs once, and this
            // would leave it and nothing more (D59).
            if ('bare' in nearest && nearest.post) {
                return refuse(`${s.name} with no label in do { } ${nearest.post}: it is no loop to perl, which leaves the loop round it, or dies; label the loop it is for, and say ${s.name} NAME`, s.pos);
            }
            if ('bare' in nearest) {
                return refuse(`${s.name} with no label would leave only the bare block that begins on line ${nearest.bare.line}, to perl: label the loop it is for, and say ${s.name} NAME`, s.pos);
            }
            jumps.set(s, loops.get(nearest.loop)!);
            return;
        }
        // A `try` is no loop (T304): its block is a scope, and the catch's
        // variable is in a scope round the catch's block, so that a `my` of
        // its name there is a second variable, as in perl (T310).
        case 'try': {
            inner(s.body);
            scopes.push(new Map());
            of.set(s.var, names.length);
            isArray.push(false);
            isHash.push(false);
            names.push(s.var.name);
            declare(s.var);
            inner(s.handler);
            close();
            return;
        }
        case 'if':
            // A modifier's statement is in the scope it stands in, and is
            // written before its test; an `if` with blocks is a scope of
            // its own, for its tests.
            if (s.modifier) {
                s.arms[0]!.body.forEach(statement);
                return whole(s.arms[0]!.test);
            }
            scopes.push(new Map());
            for (const arm of s.arms) {
                whole(arm.test);
                inner(arm.body);
            }
            if (s.otherwise) inner(s.otherwise);
            close();
            return;
        default: return;
        }
    };

    program.body.forEach(statement);
    // The one value of each sub with no name that uses nothing from outside
    // it, and of each named sub with a `\&name` (D161): a file variable's
    // slot, which the program fills as it starts.
    const constants = new Map<number, number>();
    for (const f of [...subs.keys()].map(k => k + 1).filter(f => (isAnon[f] && !uses[f]) || referred.has(f))) {
        const id = names.length;
        names.push(` the sub ${f}`);
        isArray.push(false);
        isHash.push(false);
        owner[id] = 0;
        slots[id] = file;
        file += 1;
        fileSlots.add(id);
        constants.set(f, id);
    }
    const targets = [...subs.keys()].map(k => k + 1).filter(f => isAnon[f] || referred.has(f));
    // The file's own frame: its file variables first, and then the rest,
    // which were numbered from 0 before anyone knew how many those were.
    for (const id of names.keys()) {
        if (owner[id] === 0 && !fileSlots.has(id)) slots[id]! += file;
    }
    frames[0] = file + variables;
    return { of, names, isArray, isHash, slots, owner, frames, file, fileIds: fileSlots, subs, calls, lists: listSubs(subs, calls, targets), loops, jumps, each, readonly, taken,
        anonOf, parents, captures, captured, constants, subrefs, targets, capturedAt, loopVars };
};
