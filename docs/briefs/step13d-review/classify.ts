// What the compiler makes of each string: refused, with its message, or
// taken. Read by strings.py. JSON in ({ header, bodies }), JSON out.
//
//     node docs/briefs/step13d-review/classify.ts < bodies.json
import { readFileSync } from 'node:fs';
import { lex } from '../../../compiler/src/lexer.ts';
import { parse } from '../../../compiler/src/parser.ts';
import { resolve } from '../../../compiler/src/resolver.ts';
import { check } from '../../../compiler/src/checker.ts';
import { CompileError } from '../../../compiler/src/errors.ts';

const { header, bodies } = JSON.parse(readFileSync(0, 'utf8')) as { header: string; bodies: string[] };
const out = bodies.map(body => {
    const src = `${header}print "${body}";\n`;
    try {
        const tokens = lex(src);
        const at = tokens.findLastIndex(t => t.kind === 'word' && t.text === 'print');
        const s = tokens[at + 1]!;
        // The body is one string and then `;`, or it is not what was asked.
        if (s.kind !== 'str' || tokens[at + 2]?.kind !== ';' || s.text.length !== body.length + 2) return { no: 'the string ends before the body does' };
        const program = parse(tokens);
        check(program, resolve(program));
        return { ok: true };
    } catch (e) {
        if (e instanceof CompileError) return { no: e.message };
        throw e;
    }
});
process.stdout.write(JSON.stringify(out));
