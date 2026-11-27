// The fuzzer's compiler: the driver's passes (bin/curlyc.ts) over many
// programs in one process, so that a program refused, or repaired and
// asked again, costs no Node start. For each path on a line of stdin, the
// C is written to PATH.c and a line of JSON comes back: `{ ok: true }`,
// `{ at, refused }` for a refusal, or `{ internal }` for the compiler's own
// failure. run.py links the C with one prebuilt runtime, as the driver
// does under CURLY_RT_OBJ.
import { readFileSync, writeFileSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { lex } from '../../../compiler/src/lexer.ts';
import { parse } from '../../../compiler/src/parser.ts';
import { resolve } from '../../../compiler/src/resolver.ts';
import { check } from '../../../compiler/src/checker.ts';
import { generate } from '../../../compiler/src/codegen.ts';
import { CompileError } from '../../../compiler/src/errors.ts';

const rl = createInterface({ input: process.stdin });
rl.on('line', path => {
    if (path === '') return;
    let line: unknown;
    try {
        const program = parse(lex(readFileSync(path, 'utf8')));
        const names = resolve(program);
        check(program, names);
        writeFileSync(`${path}.c`, generate(program, names, path));
        line = { ok: true };
    } catch (e) {
        if (e instanceof CompileError) line = { at: `${e.line}:${e.col}`, line: e.line, refused: e.message };
        else if (e instanceof RangeError) line = { internal: 'nests too deeply' };
        else line = { internal: String((e as Error).stack).slice(0, 2000) };
    }
    process.stdout.write(JSON.stringify(line) + '\n');
});
