// For patterns.py: reads a JSON list of {body, flags} from stdin and
// writes, for each, the empty string if compiler/src/regex.ts takes it and
// its refusal's message if not.
import { readFileSync } from 'node:fs';
import { compileRegex } from '../../../compiler/src/regex.ts';
import { CompileError } from '../../../compiler/src/errors.ts';

const cases = JSON.parse(readFileSync(0, 'utf-8')) as { body: string; flags: string }[];
const at = { line: 1, col: 1 };
const out = cases.map(c => {
    try {
        compileRegex(c.body, at, c.flags, at);
        return '';
    } catch (e) {
        if (e instanceof CompileError) return e.message;
        return `internal: ${(e as Error).message}`;
    }
});
process.stdout.write(JSON.stringify(out));
