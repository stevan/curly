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
import type { AnonSub, Binder, CallRef, Class, Expr, Field, Foreach, Sort, Invoke, Isa, Jump, Loop, My, MyArray, New, Pos, Program, Stmt, Sub, SubRef } from './ast.ts';
import { listSubs } from './shapes.ts';
import { CORE_CLASSES, HELD_PACKAGES, METHOD_RESERVED, NAMES, PERL_WORDS, isVersionString } from './names.ts';

// Step 17a. A class, as the program declares it (D170 to D178): `parent`
// its index, -1 for none; `fields` its own, each with its declaration and
// its place in an instance, after every field of its parents (`base`);
// `params` its own fields' parameters, in order; `init` the function of
// its fields, and `adjusts` its `ADJUST` blocks; `methods` its own, a
// reader and a writer too, and `lexicals` its `my method`s, each by name
// to its function; `table` every method its objects answer to, its
// parent's where it has none of its own; `slot` the file declaration whose
// slot holds the class, made as the program starts.
export type ClassInfo = {
    name: string; decl: Class; parent: number;
    fields: { id: number; field: Field; index: number }[];
    params: { name: string; field: Field; required: boolean }[];
    base: number; total: number; init: number; adjusts: number[];
    methods: Map<string, number>; lexicals: Map<string, { fn: number; item: number }>; table: Map<string, number>; slot: number;
};

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
    // Step 17a. The classes, in the order declared; each method name's
    // number, by which the runtime dispatches (D172); every function a
    // method call or a `new` may run (a method call's every method of its
    // name, a `new`'s every field default and `ADJUST` of its class and
    // the parents, and for `__CLASS__->new` of every class below too,
    // D178); the class a `new` or an `isa` names; each function's `$self`
    // and class (-1 for none); and where each field is in an instance.
    classes: readonly ClassInfo[];
    classOf: ReadonlyMap<string, number>;
    methodIds: ReadonlyMap<string, number>;
    targetsOf: ReadonlyMap<Expr, readonly number[]>;
    newOf: ReadonlyMap<New, number>;
    isaOf: ReadonlyMap<Isa, number>;
    selfOf: readonly (number | undefined)[];
    fnClass: readonly number[];
    fieldOf: ReadonlyMap<number, { cls: number; index: number }>;
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
type Round = { loop: Loop } | { bare: Pos } | { wall: string };

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
    const named: Sub[] = program.body.filter(s => s.kind === 'sub');
    // Step 17a: the functions of the classes after the named subs, each
    // class's fields first and then its subs in the order written.
    const classDecls: Class[] = program.body.filter(s => s.kind === 'class');
    const subs: Sub[] = [...named, ...classDecls.flatMap(c => [c.init, ...c.body.filter(b => b.kind === 'sub')])];
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
    for (const [n, s] of named.entries()) {
        if (called.has(s.name)) refuse(`a second sub called ${s.name}: perl warns that it is redefined, and takes this one`, s.named);
        called.set(s.name, n + 1);
    }
    const calls = new Map<Invoke, number>();

    // ---- step 17a: the classes, before anything is read, since a class
    // may be used above its declaration (17-used-before).
    const classes: ClassInfo[] = [];
    const classOf = new Map<string, number>();
    const methodIds = new Map<string, number>();
    const fnClass: number[] = [-1, ...subs.map(() => -1)];
    const selfOf: (number | undefined)[] = [];
    const fieldOf = new Map<number, { cls: number; index: number }>();
    const targetsOf = new Map<Expr, readonly number[]>();
    const newOf = new Map<New, number>();
    const isaOf = new Map<Isa, number>();
    const itemOf = new Map<Sub, number>();
    {
        let fnNext = named.length + 1;
        for (const c of classDecls) {
            const parts = c.name.split('::');
            if (parts.some(p => !/^[A-Z]/.test(p))) refuse(`class ${c.name}: every part of a class's name begins with a capital letter (D178): perl takes other names for its own words, its packages or a version (T426)`, c.named);
            const own = parts.find(p => PERL_WORDS.has(p) || NAMES.has(p) || METHOD_RESERVED.has(p));
            if (own !== undefined) refuse(`class ${c.name}: ${own} is perl's own name (D178, T426)`, c.named);
            if (HELD_PACKAGES.has(parts[0]!)) refuse(`class ${c.name}: perl holds the package ${parts[0]} by the end of the preamble, and a class of it is that package or one inside it (D178, T426)`, c.named);
            if (CORE_CLASSES.has(c.name)) refuse(`class ${c.name}: Object, Role and Class are the runtime's own, held back until the metaobject protocol shows them (D177, T415)`, c.named);
            if (classOf.has(c.name)) refuse(`class ${c.name} again: perl dies, "Cannot reopen existing class" (T409)`, c.named);
            if (called.has(c.name)) refuse(`class ${c.name} and a sub of the same name: perl calls the sub, and takes what it gives for the class (T407)`, c.named);
            let parent = -1;
            if (c.isa !== undefined) {
                if (CORE_CLASSES.has(c.isa.name)) refuse(`:isa(${c.isa.name}): Object, Role and Class are held back (D177)`, c.isa.pos);
                const found = classOf.get(c.isa.name);
                if (found === undefined) refuse(`:isa(${c.isa.name}): the parent is a class declared above this one; to perl any other is a module to load (T410)`, c.isa.pos);
                parent = found!;
            }
            const base = parent < 0 ? 0 : classes[parent]!.total;
            const ownFields = c.body.filter(b => b.kind === 'field');
            const keys = new Set<string>();
            for (const f of ownFields) {
                const k = (f.var.kind === 'myarray' ? (f.var.hash ? '%' : '@') : '$') + f.var.name;
                if (keys.has(k)) refuse(`field ${k} again in one class: perl warns that it masks the first`, f.var.pos);
                keys.add(k);
            }
            const index = classes.length;
            const init = fnNext++;
            fnClass[init] = index;
            const info: ClassInfo = {
                name: c.name, decl: c, parent, fields: [], base, total: base + ownFields.length, init, adjusts: [],
                params: ownFields.filter(f => f.param !== undefined).map(f => ({ name: f.param!.name, field: f, required: f.default === undefined })),
                methods: new Map(), lexicals: new Map(), table: new Map(parent < 0 ? [] : classes[parent]!.table), slot: -1,
            };
            // A parameter's name once along the chain (17-param-collide).
            const taken_ = new Set<string>();
            for (let p = parent; p >= 0; p = classes[p]!.parent) classes[p]!.params.forEach(q => taken_.add(q.name));
            for (const q of info.params) {
                if (taken_.has(q.name)) refuse(`:param(${q.name}) where the name is a parameter of this class or a parent already: perl dies, "that name is already in use"`, q.field.param!.pos);
                taken_.add(q.name);
            }
            for (const [k, b] of c.body.entries()) {
                if (b.kind !== 'sub') continue;
                const fn = fnNext++;
                fnClass[fn] = index;
                itemOf.set(b, k);
                const how = b.method!.how;
                if (how === 'adjust') {
                    info.adjusts.push(fn);
                    continue;
                }
                const name = b.name;
                const said = how === 'lexical' ? `my method ${name}` : how === 'reader' ? `the reader ${name}` : how === 'writer' ? `the writer ${name}` : `method ${name}`;
                if (METHOD_RESERVED.has(name)) refuse(`${said}: perl gives the name a meaning of its own, and the method is not what a call of it reaches (D178, T409, T416, T423)`, b.named);
                if (name.startsWith('__') || isVersionString(name)) refuse(`${said}: a name perl reads as one of its own words or a version`, b.named);
                if (how === 'lexical' && (PERL_WORDS.has(name) || NAMES.has(name))) refuse(`${said}: a my method of a word of perl's takes every use of the word below it (D178, T424)`, b.named);
                if (info.methods.has(name) || info.lexicals.has(name)) refuse(`${said} again in class ${c.name}: perl warns that it is redefined, and takes the last (T409)`, b.named);
                if (how === 'lexical') info.lexicals.set(name, { fn, item: k });
                else {
                    info.methods.set(name, fn);
                    info.table.set(name, fn);
                    if (!methodIds.has(name)) methodIds.set(name, methodIds.size);
                }
            }
            classes.push(info);
            classOf.set(c.name, index);
        }
        // A method named as a class is, or `N` of `C` beside a class `C::N`,
        // hides the class (T425): checked once every class is known.
        for (const info of classes) {
            for (const b of info.decl.body) {
                if (b.kind !== 'sub' || b.method!.how === 'adjust') continue;
                if (classOf.has(b.name) || classOf.has(`${info.name}::${b.name}`)) {
                    refuse(`${b.method!.how === 'lexical' ? 'my method' : b.method!.how === 'reader' ? 'the reader' : b.method!.how === 'writer' ? 'the writer' : 'method'} ${b.name} where a class is called ${classOf.has(b.name) ? b.name : `${info.name}::${b.name}`}: perl takes the class's name for a call of the method (D178, T425)`, b.named);
                }
            }
        }
    }
    // The number of a class's sub.
    const fnOf = (b: Sub): number => subs.indexOf(b) + 1;
    // The class whose functions are being read (-1 for none), and the item
    // of its block being read.
    let inClass = -1;
    let inItem = -1;
    // Every field name of the class being read: no `my` or parameter may
    // take one, nor `$self` (D178, T430).
    const guardName = (d: My | MyArray): void => {
        if (inClass < 0 || d.name.startsWith(' ')) return;
        const k = (d.kind === 'myarray' ? (d.hash ? '%' : '@') : '$') + d.name;
        if (d.kind === 'my' && d.name === 'self') refuse('$self declared again in a class: perl hides the object behind it, in silence (D178, T430); choose another name', d.pos);
        const fields = classes[inClass]!.decl.body.filter(b => b.kind === 'field');
        if (fields.some(f => (f.var.kind === 'myarray' ? (f.var.hash ? '%' : '@') : '$') + f.var.name === k)) {
            refuse(`${k} declared in a class with a field ${k}: perl hides the field behind it, in silence (D178, T430); choose another name`, d.pos);
        }
    };

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
            if (found === undefined && e.name === 'self' && inClass >= 0) return refuse("$self in a field's default: perl does not compile it (T401); a field's default sees the fields above it, and an ADJUST block sees $self", e.pos);
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
            if (inClass >= 0 && !e.name.startsWith('main::')) return refuse(`\\&${e.name} in a class: perl takes the class's package's sub, \\&${classes[inClass]!.name}::${e.name} (D178, T422); write \\&main::${e.name}`, e.pos);
            const found = called.get(e.name.replace(/^main::/, ''));
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
            // `\$self` (D178, T432): to perl the variable that holds the
            // object, which a store through the reference replaces.
            if (e.of.kind === 'var' && e.of.name === 'self' && inClass >= 0) return refuse('\\$self: to perl it is the variable that holds the object, and a store through it replaces the object (D178, T432); the object itself, $self, is a reference already', e.pos);
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
        // Step 17a: a method call, its invocant first (T429); `new`; the
        // class of the object; `isa`.
        case 'methcall': {
            walk(e.invocant, declared);
            e.args.forEach(a => walk(a, declared));
            const self = e.invocant.kind === 'var' && e.invocant.name === 'self' && inClass >= 0;
            if (e.lexical) {
                if (!self) return refuse(`->&${e.name}: a my method is called on $self alone (D178, T424): perl calls it on any object, of any class, with no dispatch`, e.pos);
                const lexical = classes[inClass]!.lexicals.get(e.name);
                if (lexical === undefined) return refuse(`->&${e.name}: class ${classes[inClass]!.name} has no my method called ${e.name}; perl calls the sub of that name in the class's package, with no dispatch (D178, T424)`, e.pos);
                if (lexical.item > inItem) return refuse(`->&${e.name} above its my method: perl does not see it there, and dies (D178, T424); declare the my method first`, e.pos);
                targetsOf.set(e, [lexical.fn]);
                return;
            }
            if (e.super) {
                if (!self) return refuse(`->SUPER::${e.name} on what is not $self: perl takes the parent of the class it is written in whatever the object, and the language calls it on $self alone (D178, T431)`, e.pos);
                const parent = classes[inClass]!.parent;
                const fn = parent < 0 ? undefined : classes[parent]!.table.get(e.name);
                if (fn === undefined) return refuse(`->SUPER::${e.name}: ${parent < 0 ? `class ${classes[inClass]!.name} has no parent` : `no parent of ${classes[inClass]!.name} has a method called ${e.name}`}, and perl dies when the call is made`, e.pos);
                targetsOf.set(e, [fn]);
                return;
            }
            const found = classes.flatMap(c => (c.methods.has(e.name) ? [c.methods.get(e.name)!] : []));
            if (found.length === 0) return refuse(`->${e.name}: no class of the program has a method called ${e.name}, and perl dies when the call is made`, e.pos);
            targetsOf.set(e, found);
            return;
        }
        case 'new': {
            e.args.forEach(a => walk(a, declared));
            const chain = (c: number): number[] => (c < 0 ? [] : [...chain(classes[c]!.parent), c]);
            const runs = (c: number): number[] => {
                const all = chain(c);
                return [...all.map(k => classes[k]!.init), ...all.flatMap(k => classes[k]!.adjusts)];
            };
            if (e.cls === undefined) {
                if (inClass < 0 || isAnon[fn]) return refuse('__CLASS__->new outside a method, an ADJUST block or a field\'s default: perl has no object there to take the class of', e.pos);
                const below = classes.map((_, k) => k).filter(k => chain(k).includes(inClass));
                targetsOf.set(e, [...new Set(below.flatMap(runs))]);
                return;
            }
            if (CORE_CLASSES.has(e.cls)) return refuse(`${e.cls}->new: Object, Role and Class are held back (D177)`, e.pos);
            const c = classOf.get(e.cls);
            if (c === undefined) return refuse(`${e.cls}->new: the program has no class called ${e.cls}`, e.pos);
            newOf.set(e, c);
            targetsOf.set(e, runs(c));
            return;
        }
        case 'curclass':
            if (inClass < 0 || isAnon[fn]) return refuse('__CLASS__ outside a method, an ADJUST block or a field\'s default: perl does not compile it there', e.pos);
            return;
        case 'isa': {
            walk(e.left, declared);
            if (CORE_CLASSES.has(e.cls)) return refuse(`isa ${e.cls}: Object, Role and Class are held back until the metaobject protocol shows them (D177, T415)`, e.pos);
            const c = classOf.get(e.cls);
            if (c === undefined) return refuse(`isa ${e.cls}: the program has no class called ${e.cls}; perl gives false for any other name (17-isa)`, e.pos);
            isaOf.set(e, c);
            return;
        }
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
            // Step 17a: in a class a call by name is of the class's package
            // to perl, `P::helper`, which dies (T422); `main::helper(...)`
            // is the program's sub.
            if (e.name.includes('::') && !e.name.startsWith('main::')) return refuse(`${e.name}(...): a sub of another package, or a method called as a function, which is not in the language (T411); call a method as $obj->m(...)`, e.pos);
            if (e.name.startsWith('main::') && e.name.slice(6).includes('::')) return refuse(`${e.name}(...): a sub of another package is not in the language`, e.pos);
            const bare = e.name.replace(/^main::/, '');
            if (inClass >= 0 && bare === e.name && called.has(bare)) return refuse(`${e.name}(...) in a class: perl looks it up in the class's package, ${classes[inClass]!.name}::${e.name}, and dies there (D178, T422); write main::${e.name}(...)`, e.pos);
            const found = called.get(bare);
            if (found === undefined) return refuse(`the program has no sub called ${bare}`, e.pos);
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
            guardName(d);
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
        variables.forEach(guardName);
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
    // A sub of a class (step 17a), `inside` its class, the fields it sees
    // and its item in the class's block: a function of its own as a named
    // sub is, with the fields above it in a scope round its own, and its
    // `$self` first, read-only (D175).
    const function_ = (s: Sub, number?: number, inside?: { cls: number; fields: Map<string, number>; item: number }): void => {
        const outer = { fn, inScope, variables, scopes, round, peak, quoted, nest, hidden, inClass, inItem };
        const lists = naming.splice(0);
        const chained = chains.splice(0);
        fn = number ?? called.get(s.name)!;
        inScope = 0;
        variables = 0;
        peak = 0;
        quoted = false;
        if (inside !== undefined) {
            scopes = [fileScope, new Map(inside.fields), new Map()];
            round = [];
            nest = [0, fn];
            hidden = new Set();
            inClass = inside.cls;
            inItem = inside.item;
            declareSelf(s.method!.how === 'init' ? ' self' : 'self', s.pos);
        } else if (number === undefined) {
            scopes = [fileScope, new Map()];
            round = [];
            nest = [0, fn];
            inClass = -1;
            inItem = -1;
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
            if (p.rest !== undefined) guardName(p.rest);
            if (p.my === undefined) continue;
            guardName(p.my);
            if (scopes.at(-1)!.has(p.my.name)) refuse(`two parameters called $${p.my.name}: perl warns that the second masks the first`, p.my.pos);
            of.set(p.my, names.length);
            isArray.push(false);
            isHash.push(false);
            names.push(p.my.name);
            declare(p.my);
        }
        if (s.method?.how === 'init') fields(inside!);
        else s.body.forEach(statement);
        frames[fn] = variables;
        ({ fn, inScope, variables, scopes, round, peak, quoted, nest, hidden, inClass, inItem } = outer);
        naming.push(...lists);
        chains.push(...chained);
    };

    // `$self`, in the scope of a class's function before its parameters.
    const declareSelf = (name: string, at: Pos): void => {
        const d: My = { kind: 'my', name, pos: at };
        of.set(d, names.length);
        isArray.push(false);
        isHash.push(false);
        names.push(name);
        declare(d);
        readonly.add(of.get(d)!);
        selfOf[fn] = of.get(d);
    };

    // The fields of a class, in its function `init` (step 17a): each
    // default read with the fields above it in scope (T401, T430), and then
    // the field declared, a declaration of no function's, `owner` -1, whose
    // slot is its place in an instance. What each item of the block sees is
    // kept, for the subs, which are read after.
    const seenBy = new Map<Sub, Map<string, number>>();
    const fields = (inside: { cls: number; fields: Map<string, number> }): void => {
        const info = classes[inside.cls]!;
        for (const b of info.decl.body) {
            if (b.kind === 'sub') {
                seenBy.set(b, new Map(inside.fields));
                continue;
            }
            if (b.default !== undefined) whole(b.default);
            const id = names.length;
            of.set(b.var, id);
            isArray.push(b.var.kind === 'myarray');
            isHash.push(b.var.kind === 'myarray' && b.var.hash === true);
            names.push(b.var.name);
            owner[id] = -1;
            const index = info.base + info.fields.length;
            slots[id] = index;
            info.fields.push({ id, field: b, index });
            fieldOf.set(id, { cls: inside.cls, index });
            inside.fields.set(key(b.var), id);
            scopes[1]!.set(key(b.var), id);
        }
    };

    // perl's `last` in a `map` block leaves the loop round the `map`, and
    // warns (T59).
    const walled = (word: string, op: string): string => (op === 'anon'
        ? `${word} out of a sub with no name: perl leaves the loop of whatever called the sub, and warns (D165); give back a value that says to, and test it in the loop`
        : `${word} out of the block of a ${op}: a loop says it`);

    const statement = (s: Stmt): void => {
        switch (s.kind) {
        case 'sub': return function_(s);
        // Step 17a: a class's fields, then its subs, each seeing the fields
        // above it; its slot, a file declaration holding the class.
        case 'class': {
            const c = classOf.get(s.name)!;
            const info = classes[c]!;
            function_(s.init, info.init, { cls: c, fields: new Map(), item: -1 });
            for (const [k, b] of s.body.entries()) {
                if (b.kind !== 'sub') continue;
                function_(b, fnOf(b), { cls: c, fields: seenBy.get(b)!, item: k });
            }
            return;
        }
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
            bind(s, [s.var], arrays, chained);
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
            guardName(s.var);
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
    // Each class's slot (step 17a): a file variable's, which the program
    // fills as it starts, before anything else runs.
    for (const info of classes) {
        const id = names.length;
        names.push(` the class ${info.name}`);
        isArray.push(false);
        isHash.push(false);
        owner[id] = 0;
        slots[id] = file;
        file += 1;
        fileSlots.add(id);
        info.slot = id;
    }
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
    return { of, names, isArray, isHash, slots, owner, frames, file, fileIds: fileSlots, subs, calls, lists: listSubs(subs, calls, targets, targetsOf), loops, jumps, each, readonly, taken,
        anonOf, parents, captures, captured, constants, subrefs, targets, capturedAt, loopVars,
        classes, classOf, methodIds, targetsOf, newOf, isaOf, selfOf, fnClass, fieldOf };
};
