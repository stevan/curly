// A pattern to a program for the runtime's matcher (step 19; D226 to
// D237): read, every construct outside the subset refused where it stands
// with a message that names it, and written as a row of instructions that
// runtime/regex.c runs. The matcher backtracks in perl's order of trying
// (leftmost first, an alternative before the next, a greedy count before
// a shorter and a lazy one after), so that the match found, and what each
// group captures, is perl's; what perl decides by rules of its own that a
// plain backtracking machine does not have is refused here (D231).
import { refuse } from './errors.ts';
import type { Pos } from './ast.ts';

// The instructions, as runtime/regex.c numbers them.
export const OP = {
    MATCH: 0, CHAR: 1, CHARI: 2, ANY: 3, ANYNL: 4, CLASS: 5, BOL: 6, MBOL: 7, EOL: 8, MEOL: 9, EOS: 10,
    WORDB: 11, NWORDB: 12, SPLIT: 13, JMP: 14, SAVE: 15, BACKREF: 16, BACKREFI: 17,
} as const;

// A class's flags in its row of the table: negated, then which of perl's
// classes it holds.
const NEGATED = 1;
const ESC_BIT: Readonly<Record<string, number>> = { d: 2, w: 4, s: 8, D: 16, W: 32, S: 64 };

// What a pattern is compiled to. `code` is the program; `classes` every
// class's row, `[flags, count, lo, hi, ...]`, at the offset its CLASS
// instruction gives; `groups` how many groups capture.
export type Regex = { code: number[]; classes: number[]; groups: number; icase: boolean; global: boolean };

type Node =
    | { k: 'char'; c: number }
    | { k: 'any' }
    | { k: 'class'; neg: boolean; ranges: [number, number][]; escapes: string[] }
    | { k: 'assert'; a: '^' | '$' | 'A' | 'z' | 'Z' | 'b' | 'B' }
    | { k: 'group'; n: number; body: Node }
    | { k: 'seq'; items: Node[] }
    | { k: 'alt'; alts: Node[] }
    | { k: 'rep'; body: Node; min: number; max: number; lazy: boolean }
    | { k: 'backref'; n: number };

const COUNT_MAX = 32766;
const PROGRAM_MAX = 100000;
// What perl's /x takes for a blank past ASCII (D237).
const WIDE_BLANKS = new Set([0x85, 0x200E, 0x200F, 0x2028, 0x2029]);
const FLAGS = 'imsxg';
const LATER_FLAGS: Readonly<Record<string, string>> = {
    a: '/a', u: '/u', l: '/l', n: '/n', p: '/p', o: '/o', d: '/d', e: '/e, which is s///e', r: '/r, which is s///r', c: '/c, which goes with pos',
};

const isDigit = (c: number) => c >= 0x30 && c <= 0x39;
const isHex = (c: number) => isDigit(c) || (c >= 0x41 && c <= 0x46) || (c >= 0x61 && c <= 0x66);
const isAlnum = (c: number) => isDigit(c) || (c >= 0x41 && c <= 0x5A) || (c >= 0x61 && c <= 0x7A);
const isBlankX = (c: number) => c === 0x20 || c === 0x09 || c === 0x0A;
const show = (c: number) => String.fromCodePoint(c);

// `body` is the pattern as written between its delimiters, `at` where its
// first character stands, `flags` the letters after it, `flagsAt` theirs.
export const compileRegex = (body: string, at: Pos, flags: string, flagsAt: Pos): Regex => {
    // ---- the flags
    const seen = new Set<string>();
    for (const f of flags) {
        if (seen.has(f)) refuse(f === 'x' ? '/xx in a pattern is not in the language' : `/${f} given twice`, flagsAt);
        seen.add(f);
        if (FLAGS.includes(f)) continue;
        if (LATER_FLAGS[f] !== undefined) refuse(`the flag ${LATER_FLAGS[f]} is not in the language (D226)`, flagsAt);
        refuse(`'${f}' after a pattern is no flag of perl's: perl does not compile it`, flagsAt);
    }
    const icase = seen.has('i'), multi = seen.has('m'), single = seen.has('s'), extended = seen.has('x');

    // ---- the characters, each with where it stands
    const cs: number[] = [];
    const ps: Pos[] = [];
    {
        let line = at.line, col = at.col;
        for (const ch of body) {
            const c = ch.codePointAt(0)!;
            cs.push(c);
            ps.push({ line, col });
            if (c === 0x0A) { line += 1; col = 1; } else col += 1;
        }
    }
    const end = cs.length;
    let i = 0;
    const here = (k = i): Pos => ps[k] ?? (ps.length ? { line: ps.at(-1)!.line, col: ps.at(-1)!.col + 1 } : at);
    const peek = (k = 0): number => cs[i + k] ?? -1;
    let groups = 0;
    const closed = new Set<number>();
    for (const c of cs) if (WIDE_BLANKS.has(c)) refuse(`U+${c.toString(16).toUpperCase().padStart(4, '0')} in a pattern: perl's /x takes it for a blank (D237); write it as \\x{${c.toString(16).toUpperCase()}}`, here(cs.indexOf(c)));

    // Under /x the blanks and comments between pieces go (D237).
    const skip = (): void => {
        if (!extended) return;
        for (;;) {
            if (isBlankX(peek())) i += 1;
            else if (peek() === 0x23) { while (i < end && peek() !== 0x0A) i += 1; }
            else return;
        }
    };

    const literal = (c: number, where: Pos): Node => {
        if (icase && c > 0x7F) refuse('a character past ASCII in a pattern under /i: perl folds it by Unicode\'s tables, one character to two (D230, T546)', where);
        return { k: 'char', c };
    };

    // A character's escape, the backslash at `k` and the letter next; or
    // undefined if it is not one.
    const charEscape = (k: number, inClass: boolean): number | undefined => {
        const c = peek();
        const one: Readonly<Record<string, number>> = { n: 10, t: 9, r: 13, f: 12, e: 27, a: 7 };
        const ch = c >= 0 ? show(c) : '';
        if (one[ch] !== undefined) { i += 1; return one[ch]; }
        if (ch === 'x') {
            i += 1;
            if (peek() === 0x7B) {
                i += 1;
                const from = i;
                while (i < end && isHex(peek())) i += 1;
                if (i === from || peek() !== 0x7D) refuse('\\x{...} in a pattern holds hex digits and nothing else', here(k));
                const v = parseInt(String.fromCodePoint(...cs.slice(from, i)), 16);
                i += 1;
                return checkChar(v, k);
            }
            const from = i;
            while (i < end && i < from + 2 && isHex(peek())) i += 1;
            if (i === from) refuse('\\x with no hex digit after it: perl reads it as a NUL; write \\x00 or \\x{...}', here(k));
            if (i === from + 1 && i < end && isAlnum(peek())) refuse('\\x and one hex digit, then a letter or a digit: write \\x{...}', here(k));
            return parseInt(String.fromCodePoint(...cs.slice(from, i)), 16);
        }
        if (ch === 'o' && cs[i + 1] === 0x7B) {
            i += 2;
            const from = i;
            while (i < end && peek() >= 0x30 && peek() <= 0x37) i += 1;
            if (i === from || peek() !== 0x7D) refuse('\\o{...} in a pattern holds octal digits and nothing else', here(k));
            const v = parseInt(String.fromCodePoint(...cs.slice(from, i)), 8);
            i += 1;
            return checkChar(v, k);
        }
        if (ch === 'N') {
            if (cs[i + 1] === 0x7B && cs[i + 2] === 0x55 && cs[i + 3] === 0x2B) {
                i += 4;
                const from = i;
                while (i < end && isHex(peek())) i += 1;
                if (i === from || peek() !== 0x7D) refuse('\\N{U+...} in a pattern holds hex digits and nothing else', here(k));
                const v = parseInt(String.fromCodePoint(...cs.slice(from, i)), 16);
                i += 1;
                return checkChar(v, k);
            }
            refuse(inClass ? '\\N in a class: only \\N{U+...} is in the language' : '\\N, and \\N{NAME}, in a pattern are not in the language: \\N{U+...} is (D226)', here(k));
        }
        if (c >= 0 && c < 0x80 && !isAlnum(c) && c !== 0x0A) { i += 1; return c; }
        return undefined;
    };
    const checkChar = (v: number, k: number): number => {
        if (v > 0x10FFFF || (v >= 0xD800 && v <= 0xDFFF)) refuse('an escape in a pattern that is no character: a surrogate, or past U+10FFFF (D42)', here(k));
        return v;
    };
    const otherEscape = (k: number, inClass: boolean): never => {
        const c = peek();
        const ch = c >= 0 ? show(c) : '';
        if (c < 0) return refuse('a backslash at the end of a pattern: perl does not compile it', here(k));
        if ('QEULul'.includes(ch)) return refuse(`\\${ch} in a pattern: the case escapes, and \\Q...\\E, are not in the language (D229)`, here(k));
        if (ch === 'c') return refuse('\\c in a pattern is not in the language: write \\x{...}', here(k));
        if (ch === 'p' || ch === 'P') return refuse(`\\${ch}{...}, a Unicode property, is not in the language yet (D226)`, here(k));
        if ('hHvVRXKG'.includes(ch)) return refuse(`\\${ch} in a pattern is not in the language yet (D226)`, here(k));
        if (ch === 'g' || ch === 'k') return refuse(`\\${ch}, a backreference by a number in braces or by a name, is not in the language yet: write \\1 to \\9 (D226)`, here(k));
        if (ch === 'b' && inClass) return refuse('\\b in a class is a backspace to perl: write \\x08', here(k));
        if (isDigit(c)) {
            if (inClass) return refuse('a digit after a backslash in a class is octal to perl: write \\x{...}', here(k));
            return refuse(c === 0x30 ? '\\0 in a pattern is octal to perl: write \\x00' : 'a backreference of two digits is octal to perl or another group: \\1 to \\9 are in (D226)', here(k));
        }
        if (c === 0x0A) return refuse('a backslash before the end of a line in a pattern: write \\n', here(k));
        if (c > 0x7F) return refuse('a backslash before a character past ASCII in a pattern: write the character alone', here(k));
        return refuse(`\\${ch} in a pattern is no escape of perl's: perl warns that it passes it through, or does not compile it`, here(k));
    };

    // `[...]`, the `[` taken at `k`.
    const parseClass = (k: number): Node => {
        let neg = false;
        if (peek() === 0x5E) { neg = true; i += 1; }
        if (peek() === 0x5D) refuse("']' first in a class: perl takes it for a character of the class; write \\]", here());
        const ranges: [number, number][] = [];
        const escapes: string[] = [];
        let first = true;
        // One item: a character, or one of perl's classes (a string).
        const item = (): number | string => {
            const k2 = i;
            const c = peek();
            if (c === 0x5C) {
                i += 1;
                const e = peek();
                if (e >= 0 && 'dwsDWS'.includes(show(e))) { i += 1; return show(e); }
                const v = charEscape(k2, true);
                if (v === undefined) otherEscape(k2, true);
                if (icase && v! > 0x7F) refuse('a character past ASCII in a pattern under /i: perl folds it by Unicode\'s tables, one character to two (D230, T546)', here(k2));
                return v!;
            }
            if (c === 0x5B) refuse("'[' in a class: perl may take it for a POSIX class, [:alpha:]; write \\[", here());
            if (c === 0x24 || c === 0x40) refuse(`'${show(c)}' in a class: perl may take it for a variable (D229); write \\${show(c)}`, here());
            i += 1;
            if (icase && c > 0x7F) refuse('a character past ASCII in a pattern under /i: perl folds it by Unicode\'s tables, one character to two (D230, T546)', here(k2));
            return c;
        };
        for (;;) {
            if (i >= end) refuse("a '[' with no ']' after it in the pattern: perl does not compile it", here(k));
            if (peek() === 0x5D) { i += 1; break; }
            const at0 = i;
            // `-` first or last is itself.
            if (peek() === 0x2D && (first || cs[i + 1] === 0x5D)) {
                if (first && cs[i + 1] === 0x2D) refuse("'--' first in a class: perl reads a range from '-' there; write \\-", here());
                i += 1;
                ranges.push([0x2D, 0x2D]);
                first = false;
                continue;
            }
            const lo = item();
            first = false;
            if (peek() === 0x2D && cs[i + 1] !== 0x5D && i + 1 < end) {
                i += 1;
                const hiAt = i;
                const hi = item();
                if (typeof lo === 'string' || typeof hi === 'string') refuse('a range with one of perl\'s classes at an end: perl warns, False [] range; write the - as \\-', here(at0));
                if ((lo as number) > (hi as number)) refuse(`a range backwards, ${show(lo as number)}-${show(hi as number)}: perl does not compile it`, here(hiAt));
                ranges.push([lo as number, hi as number]);
                continue;
            }
            if (typeof lo === 'string') escapes.push(lo);
            else ranges.push([lo, lo]);
        }
        if (icase) {
            for (const [lo, hi] of [...ranges]) {
                const a = Math.max(lo, 0x41), b = Math.min(hi, 0x5A);
                if (a <= b) ranges.push([a + 32, b + 32]);
                const c = Math.max(lo, 0x61), d = Math.min(hi, 0x7A);
                if (c <= d) ranges.push([c - 32, d - 32]);
            }
        }
        return { k: 'class', neg, ranges, escapes };
    };

    const nullable = (n: Node): boolean => {
        switch (n.k) {
        case 'char': case 'any': case 'class': return false;
        case 'assert': return true;
        case 'group': return nullable(n.body);
        case 'seq': return n.items.every(nullable);
        case 'alt': return n.alts.some(nullable);
        case 'rep': return n.min === 0 || nullable(n.body);
        // A backreference to an empty capture is empty.
        case 'backref': return true;
        }
    };
    const hasGroup = (n: Node): boolean => {
        switch (n.k) {
        case 'group': return n.n > 0 || hasGroup(n.body);
        case 'seq': return n.items.some(hasGroup);
        case 'alt': return n.alts.some(hasGroup);
        case 'rep': return hasGroup(n.body);
        default: return false;
        }
    };

    // A quantifier after an atom, if one comes; `k` is where the atom began.
    const quantified = (atom: Node, k: number): Node => {
        skip();
        const q = peek();
        const qAt = i;
        let min: number, max: number;
        if (q === 0x2A) { min = 0; max = -1; i += 1; }
        else if (q === 0x2B) { min = 1; max = -1; i += 1; }
        else if (q === 0x3F) { min = 0; max = 1; i += 1; }
        else if (q === 0x7B) {
            const counts = braces();
            if (counts === undefined) refuse("a '{' in a pattern that is no quantifier's: perl warns, or passes it through; write \\{", here(qAt));
            [min, max] = counts!;
        } else return atom;
        let lazy = false;
        if (peek() === 0x3F) {
            if (min === max) refuse(`a ? after {${min}}: perl warns that it is a useless greediness modifier`, here(i));
            lazy = true;
            i += 1;
        }
        else if (peek() === 0x2B) refuse('a possessive quantifier is not in the language yet (D226)', here(i));
        skip();
        const again = peek();
        if (again === 0x2A || again === 0x2B || again === 0x3F || (again === 0x7B && isDigit(cs[i + 1] ?? -1))) {
            refuse('a quantifier after a quantifier: perl does not compile it (Nested quantifiers); bracket the first, (?:...)', here(i));
        }
        if (nullable(atom)) refuse('a quantifier on what can match the empty string: perl warns, or stops by rules of its own (D231, T552)', here(qAt));
        if (hasGroup(atom) && !(atom.k === 'group' && !hasGroup(atom.body))) {
            refuse('a group that captures inside a repeated group: perl keeps or forgets its value by rules of its own (D231, T540); capture the whole repeat, ((?:...)*)', here(k));
        }
        return { k: 'rep', body: atom, min, max, lazy };
    };
    // `{n}`, `{n,}` or `{n,m}`, at a `{`; undefined if it is not one.
    // Blanks in the braces and `{,n}` are quantifiers to perl 5.42 (T542),
    // and refused.
    const braces = (): [number, number] | undefined => {
        const k = i;
        let j = i + 1;
        const digits = (): string => {
            const from = j;
            while (j < end && isDigit(cs[j]!)) j += 1;
            return String.fromCodePoint(...cs.slice(from, j));
        };
        const close = cs.indexOf(0x7D, j);
        const inside = close < 0 ? '' : String.fromCodePoint(...cs.slice(j, close));
        if (/^\s*(\d*\s*,\s*\d+|\d+\s*(,\s*\d*)?)\s*$/.test(inside) && !/^(\d+|\d+,\d*)$/.test(inside)) {
            refuse(/^\s*,/.test(inside) ? '{,n} in a pattern is {0,n} to perl 5.42: write {0,n} (D236, T542)' : 'blanks in a quantifier\'s braces: perl 5.42 takes them (D236, T542); write them hard together', here(k));
        }
        const a = digits();
        if (a === '') return undefined;
        let b = a;
        if (cs[j] === 0x2C) { j += 1; b = digits(); if (b === '') b = '-1'; }
        if (cs[j] !== 0x7D) return undefined;
        i = j + 1;
        const min = Number(a), max = Number(b);
        if (min > COUNT_MAX || max > COUNT_MAX) refuse(`a count past ${COUNT_MAX} in a pattern (D236)`, here(k));
        if (max >= 0 && min > max) refuse('{n,m} with n greater than m: perl warns that it cannot match', here(k));
        return [min, max];
    };

    const parseAtom = (): Node | undefined => {
        skip();
        const k = i;
        const c = peek();
        if (c < 0 || c === 0x7C || c === 0x29) return undefined;
        i += 1;
        switch (c) {
        case 0x28: {
            let n = 0;
            if (peek() === 0x3F) {
                const next = cs[i + 1] ?? -1;
                if (next !== 0x3A) {
                    const two = String.fromCodePoint(...cs.slice(i + 1, i + 3));
                    const what = two.startsWith('=') || two.startsWith('!') || two === '<=' || two === '<!' ? 'lookaround is not in the language yet (D226)'
                        : two.startsWith('#') ? '(?#...) is not in the language: under /x a comment is # to the end of the line'
                        : two.startsWith('<') || two.startsWith("'") || two.startsWith('P') ? 'a named capture is not in the language yet (D226)'
                        : two.startsWith('>') ? 'an atomic group is not in the language yet (D226)'
                        : two.startsWith('{') || two.startsWith('?') ? 'code in a pattern is cut'
                        : '(?...) is not in the language: of its forms, (?:...) is (D226)';
                    refuse(what, here(k));
                }
                i += 2;
            } else {
                n = ++groups;
            }
            const inner = parseAlt();
            if (peek() !== 0x29) refuse("a '(' with no ')' after it in the pattern: perl does not compile it", here(k));
            i += 1;
            if (n > 0) closed.add(n);
            return n > 0 ? { k: 'group', n, body: inner } : inner.k === 'char' || inner.k === 'any' || inner.k === 'class' ? inner : { k: 'group', n: 0, body: inner };
        }
        case 0x2E: return { k: 'any' };
        case 0x5B: return parseClass(k);
        case 0x5E: return { k: 'assert', a: '^' };
        case 0x24: {
            const next = peek();
            // (Under /x a blank or a comment after it too: perl takes no
            // variable there.)
            if (next >= 0 && next !== 0x29 && next !== 0x7C && !(extended && (isBlankX(next) || next === 0x23))) refuse("a '$' in a pattern that is not at its end, or before ')' or '|': perl may take it for a variable (D229, T550); write \\$ for the character", here(k));
            return { k: 'assert', a: '$' };
        }
        case 0x40: return refuse("'@' in a pattern: perl may take it for an array (D229); write \\@", here(k));
        case 0x2A: case 0x2B: case 0x3F: return refuse('a quantifier with nothing before it: perl does not compile it', here(k));
        case 0x7B: return refuse("a '{' in a pattern that is no quantifier's: perl warns, or passes it through; write \\{", here(k));
        case 0x7D: return refuse("a '}' in a pattern: write \\}", here(k));
        case 0x5C: {
            const e = peek();
            const ch = e >= 0 ? show(e) : '';
            if (ch !== '' && 'dwsDWS'.includes(ch)) { i += 1; return { k: 'class', neg: false, ranges: [], escapes: [ch] }; }
            if (ch !== '' && 'bBAzZ'.includes(ch)) { i += 1; return { k: 'assert', a: ch as 'b' }; }
            if (isDigit(e) && e !== 0x30 && !isDigit(cs[i + 1] ?? -1)) {
                i += 1;
                const n = e - 0x30;
                if (!closed.has(n)) refuse(n > groups ? `\\${n} names a group the pattern does not have, or not yet: perl does not compile it (T551)` : `\\${n} inside the group it names: write it after the group closes`, here(k));
                return { k: 'backref', n };
            }
            const v = charEscape(k, false);
            if (v === undefined) return otherEscape(k, false);
            return literal(v, here(k));
        }
        default:
            return literal(c, here(k));
        }
    };

    const parseSeq = (): Node => {
        const items: Node[] = [];
        for (;;) {
            const k = i;
            const atom = parseAtom();
            if (atom === undefined) break;
            items.push(quantified(atom, k));
        }
        skip();
        return items.length === 1 ? items[0]! : { k: 'seq', items };
    };
    const parseAlt = (): Node => {
        const alts = [parseSeq()];
        while (peek() === 0x7C) {
            i += 1;
            alts.push(parseSeq());
        }
        return alts.length === 1 ? alts[0]! : { k: 'alt', alts };
    };

    if (end === 0) refuse('the empty pattern: perl matches the last pattern that matched (T66)', at);
    const tree = parseAlt();
    if (i < end) refuse("a ')' with no '(' before it in the pattern: perl does not compile it", here());

    // ---- the program
    const code: number[] = [];
    const classes: number[] = [];
    const emit = (...xs: number[]): void => {
        code.push(...xs);
        if (code.length > PROGRAM_MAX) refuse(`a pattern whose program is more than ${PROGRAM_MAX} instructions (D236): fewer or smaller counts`, at);
    };
    const gen = (n: Node): void => {
        switch (n.k) {
        case 'char':
            if (icase && ((n.c >= 0x41 && n.c <= 0x5A) || (n.c >= 0x61 && n.c <= 0x7A))) emit(OP.CHARI, n.c | 0x20);
            else emit(OP.CHAR, n.c);
            return;
        case 'any': emit(single ? OP.ANYNL : OP.ANY); return;
        case 'class': {
            const off = classes.length;
            let flags = n.neg ? NEGATED : 0;
            for (const e of n.escapes) flags |= ESC_BIT[e]!;
            classes.push(flags, n.ranges.length, ...n.ranges.flat());
            emit(OP.CLASS, off);
            return;
        }
        case 'assert': {
            const op = n.a === '^' ? (multi ? OP.MBOL : OP.BOL) : n.a === '$' ? (multi ? OP.MEOL : OP.EOL)
                : n.a === 'A' ? OP.BOL : n.a === 'z' ? OP.EOS : n.a === 'Z' ? OP.EOL : n.a === 'b' ? OP.WORDB : OP.NWORDB;
            emit(op);
            return;
        }
        case 'group':
            if (n.n > 0) emit(OP.SAVE, 2 * n.n);
            gen(n.body);
            if (n.n > 0) emit(OP.SAVE, 2 * n.n + 1);
            return;
        case 'seq': n.items.forEach(gen); return;
        case 'alt': {
            const jumps: number[] = [];
            n.alts.forEach((a, k) => {
                if (k < n.alts.length - 1) {
                    const split = code.length;
                    emit(OP.SPLIT, split + 3, 0);
                    gen(a);
                    jumps.push(code.length);
                    emit(OP.JMP, 0);
                    code[split + 2] = code.length;
                } else gen(a);
            });
            for (const j of jumps) code[j + 1] = code.length;
            return;
        }
        case 'rep': {
            for (let k = 0; k < n.min; k++) gen(n.body);
            if (n.max < 0) {
                const top = code.length;
                emit(OP.SPLIT, 0, 0);
                gen(n.body);
                emit(OP.JMP, top);
                const out = code.length;
                code[top + 1] = n.lazy ? out : top + 3;
                code[top + 2] = n.lazy ? top + 3 : out;
                return;
            }
            const splits: number[] = [];
            for (let k = n.min; k < n.max; k++) {
                splits.push(code.length);
                emit(OP.SPLIT, 0, 0);
                gen(n.body);
            }
            const out = code.length;
            for (const s of splits) {
                code[s + 1] = n.lazy ? out : s + 3;
                code[s + 2] = n.lazy ? s + 3 : out;
            }
            return;
        }
        case 'backref': emit(icase ? OP.BACKREFI : OP.BACKREF, n.n); return;
        }
    };
    emit(OP.SAVE, 0);
    gen(tree);
    emit(OP.SAVE, 1, OP.MATCH);
    return { code, classes, groups, icase, global: seen.has('g') };
};
