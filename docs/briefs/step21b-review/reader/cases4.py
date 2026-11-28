# Step 21a's second reader's cases (stdin where a list or a value is decided, the order of reads, loop tests,
# subs that give lines back), with a file's handle for STDIN, the file holding what stdin held.
import importlib.util, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'step21-review', 'reader') + '/'
CASES = []
for n in (1, 2, 7, 8, 9, 10):
    spec = importlib.util.spec_from_file_location('c', R + f'cases{n}.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for c in m.CASES:
        if isinstance(c, str): c = {'p': c}
        if 'STDIN' not in c['p'] or c.get('args') or c.get('env'): continue
        stdin = c.get('stdin', b'a\nb\nc\n')
        if isinstance(stdin, str): stdin = stdin.encode()
        p = c['p'].replace('<STDIN>', '<$fh>').replace('eof(STDIN)', 'eof($fh)').replace('eof STDIN', 'eof($fh)')
        pre = 'use v5.42;\n' + c.get('pre', '') + ("use open ':std', ':encoding(UTF-8)';\n" if c.get('open') else '')
        CASES.append({'p': "open(my $fh, '<', 'f.txt') or die \"no\\n\";\n" + p, 'pre': pre, 'files': {'f.txt': stdin}})
