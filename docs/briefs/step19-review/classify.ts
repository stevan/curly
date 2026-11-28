// For differential.py (the independent review of step 19): reads a JSON
// list of programs from stdin and writes, for each, the empty string if
// the whole front end takes it (lexer, parser, resolver, checker: the
// passes bin/curlyc.ts runs before it writes any C) and the refusal's
// message if not. Unlike refusals.ts beside it, which asks regex.ts
// alone, this goes through the lexer's choice of where a pattern ends.
import { readFileSync } from 'node:fs';
import { lex } from '../../../compiler/src/lexer.ts';
import { parse } from '../../../compiler/src/parser.ts';
import { resolve } from '../../../compiler/src/resolver.ts';
import { check } from '../../../compiler/src/checker.ts';
import { CompileError } from '../../../compiler/src/errors.ts';

const cases = JSON.parse(readFileSync(0, 'utf-8')) as string[];
const out = cases.map(text => {
    try {
        const program = parse(lex(text));
        check(program, resolve(program));
        return '';
    } catch (e) {
        if (e instanceof CompileError) return e.message;
        return `internal: ${(e as Error).message}`;
    }
});
process.stdout.write(JSON.stringify(out));
