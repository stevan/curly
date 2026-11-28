#!/usr/bin/env python3
"""t/6400 to t/6412, t/6420 to t/6432, and the faults t/6440 to t/6489:
files and handles (step 21b; D270 to D283).

The definition, which is all this file knows of them. A file is bytes, and
a handle a record of which file, which way, how far, and how many lines it
has given:

  open(my $fh, MODE, NAME)    `<` reads a file that is there; `>` makes it
                              empty, `>>` adds to it, and both make one
                              that is not there. 1, or undef when the file
                              is not there to read. The variable holds a
                              handle either way; one it held is opened
                              again, and every copy of it sees that
  <$fh>, one value wanted     the next line, its newline kept, or undef
  <$fh>, a list wanted        every line that is left
  eof($fh)                    no line is left
  print/say/printf $fh LIST   written to the file, in order; `{ EXPR }`
                              for `$fh` too
  close($fh)                  1; the count of lines is 0 again
  a line                      without `use open` each byte a character,
                              with it UTF-8, as stdin's are
  errno                       25 (ENOTTY) after an open that worked, the
                              system's number after one that failed (2,
                              ENOENT), 0 after a read that met the end of
                              its input for the first time; eof() changes
                              nothing, and the end, once met, is not
                              looked for again
  $!                          the system's words for errno, while the last
                              open is one that failed; else a fault
  die, uncaught               exits with errno when it is not 0, else 255
  a message with no newline   ends ` at FILE line N.`, and names stdin
                              (`, <STDIN> line N`) when stdin was read
                              last and has given a line; when a file's
                              handle was read last, has given a line and
                              was not closed since, a fault

perl is the second derivation (t/checks.py oracle). A test's files are its
`# file:` headers, which t/run.sh and the oracle put in the directory the
run is in, for perl and the program alike (D282).

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/file.py --program 6400 > t/6400-file-lines.pl
    python3 t/models/file.py 6400 > t/6400-file-lines.expected
    python3 t/models/file.py --program 6401 > t/6401-file-lists.pl
    python3 t/models/file.py 6401 > t/6401-file-lists.expected
    python3 t/models/file.py --program 6402 > t/6402-file-while.pl
    python3 t/models/file.py 6402 > t/6402-file-while.expected
    python3 t/models/file.py --program 6403 > t/6403-file-write.pl
    python3 t/models/file.py 6403 > t/6403-file-write.expected
    python3 t/models/file.py --program 6404 > t/6404-file-handles-as-values.pl
    python3 t/models/file.py 6404 > t/6404-file-handles-as-values.expected
    python3 t/models/file.py --program 6405 > t/6405-file-open-fails.pl
    python3 t/models/file.py 6405 > t/6405-file-open-fails.expected
    python3 t/models/file.py --program 6406 > t/6406-file-bytes.pl
    python3 t/models/file.py 6406 > t/6406-file-bytes.expected
    python3 t/models/file.py --program 6407 > t/6407-file-utf8.pl
    python3 t/models/file.py 6407 > t/6407-file-utf8.expected
    python3 t/models/file.py --program 6408 > t/6408-file-dropped-handles.pl
    python3 t/models/file.py 6408 > t/6408-file-dropped-handles.expected
    python3 t/models/file.py --program 6409 > t/6409-file-many-handles.pl
    python3 t/models/file.py 6409 > t/6409-file-many-handles.expected
    python3 t/models/file.py --program 6410 > t/6410-file-and-stdin.pl
    python3 t/models/file.py 6410 > t/6410-file-and-stdin.expected
    python3 t/models/file.py --program 6411 > t/6411-file-formats.pl
    python3 t/models/file.py 6411 > t/6411-file-formats.expected
    python3 t/models/file.py --program 6412 > t/6412-file-or-die.pl
    python3 t/models/file.py 6412 > t/6412-file-or-die.expected
    python3 t/models/file.py --program 6420 > t/6420-exit-open-worked.pl
    python3 t/models/file.py 6420 > t/6420-exit-open-worked.expected
    python3 t/models/file.py --program 6421 > t/6421-exit-open-failed.pl
    python3 t/models/file.py 6421 > t/6421-exit-open-failed.expected
    python3 t/models/file.py --program 6422 > t/6422-exit-read-to-the-end.pl
    python3 t/models/file.py 6422 > t/6422-exit-read-to-the-end.expected
    python3 t/models/file.py --program 6423 > t/6423-exit-read-some.pl
    python3 t/models/file.py 6423 > t/6423-exit-read-some.expected
    python3 t/models/file.py --program 6424 > t/6424-exit-eof-met-the-end.pl
    python3 t/models/file.py 6424 > t/6424-exit-eof-met-the-end.expected
    python3 t/models/file.py --program 6425 > t/6425-exit-list-to-the-end.pl
    python3 t/models/file.py 6425 > t/6425-exit-list-to-the-end.expected
    python3 t/models/file.py --program 6426 > t/6426-exit-last-line-cut.pl
    python3 t/models/file.py 6426 > t/6426-exit-last-line-cut.expected
    python3 t/models/file.py --program 6427 > t/6427-exit-written.pl
    python3 t/models/file.py 6427 > t/6427-exit-written.expected
    python3 t/models/file.py --program 6428 > t/6428-exit-stdin-to-the-end.pl
    python3 t/models/file.py 6428 > t/6428-exit-stdin-to-the-end.expected
    python3 t/models/file.py --program 6429 > t/6429-exit-fail-ok-fail.pl
    python3 t/models/file.py 6429 > t/6429-exit-fail-ok-fail.expected
    python3 t/models/file.py --program 6430 > t/6430-exit-closed-no-newline.pl
    python3 t/models/file.py 6430 > t/6430-exit-closed-no-newline.expected
    python3 t/models/file.py --program 6431 > t/6431-exit-after-caught.pl
    python3 t/models/file.py 6431 > t/6431-exit-after-caught.expected
    python3 t/models/file.py --program 6432 > t/6432-exit-open-after-underflow.pl
    python3 t/models/file.py 6432 > t/6432-exit-open-after-underflow.expected
    python3 t/models/file.py --program 6440 > t/6440-fault-file-close-twice.pl
    python3 t/models/file.py 6440 > t/6440-fault-file-close-twice.expected
    python3 t/models/file.py --program 6441 > t/6441-fault-file-close-never-opened.pl
    python3 t/models/file.py 6441 > t/6441-fault-file-close-never-opened.expected
    python3 t/models/file.py --program 6442 > t/6442-fault-file-read-closed.pl
    python3 t/models/file.py 6442 > t/6442-fault-file-read-closed.expected
    python3 t/models/file.py --program 6443 > t/6443-fault-file-read-list-closed.pl
    python3 t/models/file.py 6443 > t/6443-fault-file-read-list-closed.expected
    python3 t/models/file.py --program 6444 > t/6444-fault-file-read-after-failed-open.pl
    python3 t/models/file.py 6444 > t/6444-fault-file-read-after-failed-open.expected
    python3 t/models/file.py --program 6445 > t/6445-fault-file-read-write-only.pl
    python3 t/models/file.py 6445 > t/6445-fault-file-read-write-only.expected
    python3 t/models/file.py --program 6446 > t/6446-fault-file-read-append-only.pl
    python3 t/models/file.py 6446 > t/6446-fault-file-read-append-only.expected
    python3 t/models/file.py --program 6447 > t/6447-fault-file-write-closed.pl
    python3 t/models/file.py 6447 > t/6447-fault-file-write-closed.expected
    python3 t/models/file.py --program 6448 > t/6448-fault-file-say-closed.pl
    python3 t/models/file.py 6448 > t/6448-fault-file-say-closed.expected
    python3 t/models/file.py --program 6449 > t/6449-fault-file-printf-closed.pl
    python3 t/models/file.py 6449 > t/6449-fault-file-printf-closed.expected
    python3 t/models/file.py --program 6450 > t/6450-fault-file-write-read-only.pl
    python3 t/models/file.py 6450 > t/6450-fault-file-write-read-only.expected
    python3 t/models/file.py --program 6451 > t/6451-fault-file-say-read-only.pl
    python3 t/models/file.py 6451 > t/6451-fault-file-say-read-only.expected
    python3 t/models/file.py --program 6452 > t/6452-fault-file-printf-read-only.pl
    python3 t/models/file.py 6452 > t/6452-fault-file-printf-read-only.expected
    python3 t/models/file.py --program 6453 > t/6453-fault-file-eof-closed.pl
    python3 t/models/file.py 6453 > t/6453-fault-file-eof-closed.expected
    python3 t/models/file.py --program 6454 > t/6454-fault-file-eof-write-only.pl
    python3 t/models/file.py 6454 > t/6454-fault-file-eof-write-only.expected
    python3 t/models/file.py --program 6455 > t/6455-fault-file-twice-write-then-read.pl
    python3 t/models/file.py 6455 > t/6455-fault-file-twice-write-then-read.expected
    python3 t/models/file.py --program 6456 > t/6456-fault-file-twice-read-then-write.pl
    python3 t/models/file.py 6456 > t/6456-fault-file-twice-read-then-write.expected
    python3 t/models/file.py --program 6457 > t/6457-fault-file-twice-write-write.pl
    python3 t/models/file.py 6457 > t/6457-fault-file-twice-write-write.expected
    python3 t/models/file.py --program 6458 > t/6458-fault-file-twice-read-then-append.pl
    python3 t/models/file.py 6458 > t/6458-fault-file-twice-read-then-append.expected
    python3 t/models/file.py --program 6459 > t/6459-fault-file-open-directory.pl
    python3 t/models/file.py 6459 > t/6459-fault-file-open-directory.expected
    python3 t/models/file.py --program 6460 > t/6460-fault-file-open-name-nul.pl
    python3 t/models/file.py 6460 > t/6460-fault-file-open-name-nul.expected
    python3 t/models/file.py --program 6461 > t/6461-fault-file-open-name-past-ascii.pl
    python3 t/models/file.py 6461 > t/6461-fault-file-open-name-past-ascii.expected
    python3 t/models/file.py --program 6462 > t/6462-fault-file-open-name-undef.pl
    python3 t/models/file.py 6462 > t/6462-fault-file-open-name-undef.expected
    python3 t/models/file.py --program 6463 > t/6463-fault-file-open-name-reference.pl
    python3 t/models/file.py 6463 > t/6463-fault-file-open-name-reference.expected
    python3 t/models/file.py --program 6464 > t/6464-fault-file-open-variable-number.pl
    python3 t/models/file.py 6464 > t/6464-fault-file-open-variable-number.expected
    python3 t/models/file.py --program 6465 > t/6465-fault-file-open-variable-reference.pl
    python3 t/models/file.py 6465 > t/6465-fault-file-open-variable-reference.expected
    python3 t/models/file.py --program 6466 > t/6466-fault-file-errno-no-open.pl
    python3 t/models/file.py 6466 > t/6466-fault-file-errno-no-open.expected
    python3 t/models/file.py --program 6467 > t/6467-fault-file-errno-after-success.pl
    python3 t/models/file.py 6467 > t/6467-fault-file-errno-after-success.expected
    python3 t/models/file.py --program 6468 > t/6468-fault-file-errno-after-end.pl
    python3 t/models/file.py 6468 > t/6468-fault-file-errno-after-end.expected
    python3 t/models/file.py --program 6469 > t/6469-fault-file-errno-after-stdin-end.pl
    python3 t/models/file.py 6469 > t/6469-fault-file-errno-after-stdin-end.expected
    python3 t/models/file.py --program 6470 > t/6470-fault-file-errno-as-number.pl
    python3 t/models/file.py 6470 > t/6470-fault-file-errno-as-number.expected
    python3 t/models/file.py --program 6471 > t/6471-fault-file-message-warn.pl
    python3 t/models/file.py 6471 > t/6471-fault-file-message-warn.expected
    python3 t/models/file.py --program 6472 > t/6472-fault-file-message-die.pl
    python3 t/models/file.py 6472 > t/6472-fault-file-message-die.expected
    python3 t/models/file.py --program 6473 > t/6473-fault-file-message-die-caught.pl
    python3 t/models/file.py 6473 > t/6473-fault-file-message-die-caught.expected
    python3 t/models/file.py --program 6474 > t/6474-fault-file-message-after-eof.pl
    python3 t/models/file.py 6474 > t/6474-fault-file-message-after-eof.expected
    python3 t/models/file.py --program 6475 > t/6475-fault-file-message-or-die.pl
    python3 t/models/file.py 6475 > t/6475-fault-file-message-or-die.expected
    python3 t/models/file.py --program 6476 > t/6476-fault-file-message-opened-again.pl
    python3 t/models/file.py 6476 > t/6476-fault-file-message-opened-again.expected
    python3 t/models/file.py --program 6477 > t/6477-fault-file-handle-printed.pl
    python3 t/models/file.py 6477 > t/6477-fault-file-handle-printed.expected
    python3 t/models/file.py --program 6478 > t/6478-fault-file-handle-printed-comma.pl
    python3 t/models/file.py 6478 > t/6478-fault-file-handle-printed-comma.expected
    python3 t/models/file.py --program 6479 > t/6479-fault-file-handle-in-a-string.pl
    python3 t/models/file.py 6479 > t/6479-fault-file-handle-in-a-string.expected
    python3 t/models/file.py --program 6480 > t/6480-fault-file-handle-as-number.pl
    python3 t/models/file.py 6480 > t/6480-fault-file-handle-as-number.expected
    python3 t/models/file.py --program 6481 > t/6481-fault-file-handle-as-key.pl
    python3 t/models/file.py 6481 > t/6481-fault-file-handle-as-key.expected
    python3 t/models/file.py --program 6482 > t/6482-fault-file-handle-compared.pl
    python3 t/models/file.py 6482 > t/6482-fault-file-handle-compared.expected
    python3 t/models/file.py --program 6483 > t/6483-fault-file-not-a-handle-print.pl
    python3 t/models/file.py 6483 > t/6483-fault-file-not-a-handle-print.expected
    python3 t/models/file.py --program 6484 > t/6484-fault-file-not-a-handle-read.pl
    python3 t/models/file.py 6484 > t/6484-fault-file-not-a-handle-read.expected
    python3 t/models/file.py --program 6485 > t/6485-fault-file-undef-handle-read.pl
    python3 t/models/file.py 6485 > t/6485-fault-file-undef-handle-read.expected
    python3 t/models/file.py --program 6486 > t/6486-fault-file-undef-handle-close.pl
    python3 t/models/file.py 6486 > t/6486-fault-file-undef-handle-close.expected
    python3 t/models/file.py --program 6487 > t/6487-fault-file-not-a-handle-block.pl
    python3 t/models/file.py 6487 > t/6487-fault-file-not-a-handle-block.expected
    python3 t/models/file.py --program 6488 > t/6488-fault-file-write-past-ascii.pl
    python3 t/models/file.py 6488 > t/6488-fault-file-write-past-ascii.expected
    python3 t/models/file.py --program 6489 > t/6489-fault-file-write-noncharacter.pl
    python3 t/models/file.py 6489 > t/6489-fault-file-write-noncharacter.expected
    python3 t/models/file.py --program 6490 > t/6490-fault-file-read-malformed.pl
    python3 t/models/file.py 6490 > t/6490-fault-file-read-malformed.expected
    python3 t/models/file.py --program 6491 > t/6491-fault-file-read-cut.pl
    python3 t/models/file.py 6491 > t/6491-fault-file-read-cut.expected
    python3 t/models/file.py --program 6492 > t/6492-fault-file-read-past-ascii-printed.pl
    python3 t/models/file.py 6492 > t/6492-fault-file-read-past-ascii-printed.expected
    python3 t/models/file.py --program 6493 > t/6493-fault-file-printf-count.pl
    python3 t/models/file.py 6493 > t/6493-fault-file-printf-count.expected
    python3 t/models/file.py --program 6494 > t/6494-fault-file-write-undef.pl
    python3 t/models/file.py 6494 > t/6494-fault-file-write-undef.expected
    python3 t/models/file.py --program 6495 > t/6495-fault-file-handle-as-array.pl
    python3 t/models/file.py 6495 > t/6495-fault-file-handle-as-array.expected
    python3 t/models/file.py --program 6496 > t/6496-fault-file-errno-after-underflow.pl
    python3 t/models/file.py 6496 > t/6496-fault-file-errno-after-underflow.expected
    python3 t/models/file.py --program 6497 > t/6497-fault-file-eof-not-a-handle.pl
    python3 t/models/file.py 6497 > t/6497-fault-file-eof-not-a-handle.expected
    python3 t/models/file.py --program 6498 > t/6498-fault-file-message-warn-in-a-sub.pl
    python3 t/models/file.py 6498 > t/6498-fault-file-message-warn-in-a-sub.expected
    python3 t/models/file.py --program 6499 > t/6499-fault-file-close-after-reopen-failed.pl
    python3 t/models/file.py 6499 > t/6499-fault-file-close-after-reopen-failed.expected
"""
import os
import random
import sys

FILE = 't/{name}.pl'
ENOENT = 2
ENOTTY = 25


def escape(data):
    """Bytes in printf %b's escapes, for a header."""
    out = ''
    for b in data:
        c = chr(b)
        if c == '\\':
            out += '\\\\'
        elif c == '\n':
            out += '\\n'
        elif 0x20 < b < 0x7f or (b == 0x20 and out and not out.endswith(' ')):
            out += c
        else:
            out += '\\0%03o' % b
    return out


def quote(text):
    """A Perl double-quoted literal for an ASCII string."""
    out = ''
    for c in text:
        out += {'\\': '\\\\', '"': '\\"', '$': '\\$', '@': '\\@', '\n': '\\n', '\t': '\\t', '\r': '\\r', '\0': '\\0'}.get(c, c)
    return f'"{out}"'


class Handle:
    def __init__(self):
        self.name = None
        self.mode = None        # None: not open
        self.pos = 0
        self.lines = 0
        self.ended = False


SHOW = ['sub show($s) {', '    my @o;', '    for my $i (0 .. length($s) - 1) {', '        push @o, ord(substr($s, $i, 1));', '    }',
        '    return length($s) . ":" . join(",", @o);', '}']


class World:
    """A program as it is written, and what it prints as it goes."""

    def __init__(self, name, files=None, utf8=False, stdin=None, show=False, env=None):
        self.name = name
        self.files = dict(files or {})
        self.given = dict(self.files)
        self.utf8 = utf8
        self.stdin = stdin
        self.env = env
        self.stdin_pos, self.stdin_lines, self.stdin_ended = 0, 0, False
        self.vars = {}
        self.errno, self.failed = 0, False
        self.last = None
        self.body, self.out, self.err = [], '', ''
        self.status = None
        self.prelude = (['use utf8;', "use open ':std', ':encoding(UTF-8)';"] if utf8 else []) + (SHOW if show else [])
        self.n = 0

    # ---- the program's text
    def head(self, kind=None):
        hdr = [f'# t/models/file.py {self.number}']
        if kind:
            hdr.append(f'# kind: {kind}')
        if self.stdin is not None:
            hdr.append(f'# stdin: {escape(self.stdin)}')
        if self.env:
            hdr.append(f'# env: {self.env}')
        for name, data in self.given.items():
            hdr.append(f'# file: {name}={escape(data)}')
        return hdr

    def line(self):
        """The line the next statement will stand on."""
        return len(self.head(self.kind_hint)) + 1 + len(self.prelude) + len(self.body) + 1

    def emit(self, text):
        self.body.append(text)

    def fresh(self, stem):
        self.n += 1
        return f'{stem}{self.n}'

    def say(self, text):
        if self.status is None:
            self.out += text

    # ---- characters
    def chars(self, data):
        return data.decode('utf-8') if self.utf8 else data.decode('latin-1')

    def shown(self, text):
        return f'{len(text)}:' + ','.join(str(ord(c)) for c in text)

    # ---- files
    def handle(self, var):
        return self.vars[var]

    def open(self, var, mode, name, my=True, how=';', label=None):
        # (A `my` in `open` is the statement's own, or an `if`'s test's: under
        # a modifier and in an argument it is declared first, D274.)
        if my and how in ('unless', 'value'):
            self.emit(f'my ${var};')
            my = False
        target = f'my ${var}' if my else f'${var}'
        call = f"open({target}, '{mode}', {quote(name)})"
        label = label or name
        text = {';': f'{call};',
                'or die': f'{call} or die "cannot open {label}: $!\\n";',
                '|| die': f'{call} || die "cannot open {label}: $!\\n";',
                'or die line': f'{call} or die "cannot open {label}: $!";',
                'unless': f'die "cannot open {label}: $!\\n" unless {call};',
                'if': f'if ({call}) {{ say "opened {label}" }} else {{ say "no {label}: $!" }}',
                'value': f'say defined({call}) ? "defined" : "undef";'}[how]
        at = self.line()
        self.emit(text)
        if self.status is not None:
            return
        h = self.vars.get(var) if not my else None
        if h is None:
            h = Handle()
        if how != 'if':
            self.vars[var] = h
        h.mode = None
        # (A name with a slash in it is in a directory that is not there.)
        ok = not (mode == '<' and name not in self.files) and '/' not in name
        if ok:
            if mode == '>' or name not in self.files:
                self.files[name] = b''
            h.name, h.mode, h.pos, h.ended = name, mode, 0, False
            self.errno, self.failed = ENOTTY, False
        else:
            self.errno, self.failed = ENOENT, True
        words = os.strerror(ENOENT)
        if how == 'if':
            self.say(f'opened {label}\n' if ok else f'no {label}: {words}\n')
        elif how == 'value':
            self.say('defined\n' if ok else 'undef\n')
        elif how != ';' and not ok:
            self.die_now(f'cannot open {label}: {words}' + ('' if how == 'or die line' else '\n'), at)

    def close(self, var, how=';'):
        self.emit({';': f'close(${var});', 'bare': f'close ${var};', 'or die': f'close(${var}) or die "cannot close: $!\\n";', 'value': f'say close(${var});'}[how])
        if self.status is not None:
            return
        h = self.handle(var)
        assert h.mode is not None, 'the model closes an open handle'
        h.mode, h.lines = None, 0
        if how == 'value':
            self.say('1\n')

    def read(self, h):
        """The next line of a handle, as characters, or None."""
        assert h.mode == '<', 'the model reads a handle open for reading'
        self.last = h
        if h.ended:
            return None
        data = self.files[h.name]
        end = data.find(b'\n', h.pos)
        if end < 0:
            h.ended = True
            self.errno, self.failed = 0, False
            line, h.pos = data[h.pos:], len(data)
        else:
            line, h.pos = data[h.pos:end + 1], end + 1
        if not line:
            return None
        h.lines += 1
        return self.chars(line)

    def one(self, var):
        t = self.fresh('t')
        self.emit(f'my ${t} = <${var}>; say defined ${t} ? show(${t}) : "undef";')
        if self.status is None:
            got = self.read(self.handle(var))
            self.say((self.shown(got) if got is not None else 'undef') + '\n')

    def rest(self, h):
        found = []
        while True:
            got = self.read(h)
            if got is None:
                return found
            found.append(got)

    def all(self, var, how='array'):
        a = self.fresh('a')
        if how == 'array':
            self.emit(f'my @{a} = <${var}>; say scalar(@{a}), " lines"; for my $x (@{a}) {{ say show($x) }}')
        elif how == 'split':
            self.emit(f'my (${a}, @{a}) = <${var}>; say defined ${a} ? show(${a}) : "undef", " then ", scalar(@{a});')
        elif how == 'for':
            self.emit(f'for my $x (<${var}>) {{ say "for ", show($x) }}')
        elif how == 'call':
            self.emit(f'say count(<${var}>);')
        elif how == 'while':
            self.emit(f'while (my $l = <${var}>) {{ say "while ", show($l) }}')
        if self.status is not None:
            return
        got = self.rest(self.handle(var))
        if how == 'array':
            self.say(f'{len(got)} lines\n' + ''.join(self.shown(g) + '\n' for g in got))
        elif how == 'split':
            self.say((self.shown(got[0]) if got else 'undef') + f' then {max(0, len(got) - 1)}\n')
        elif how == 'for':
            self.say(''.join(f'for {self.shown(g)}\n' for g in got))
        elif how == 'call':
            self.say(f'{len(got)}\n')
        elif how == 'while':
            self.say(''.join(f'while {self.shown(g)}\n' for g in got))

    def eof(self, var):
        self.emit(f'say eof(${var}) ? "eof" : "more";')
        if self.status is not None:
            return
        h = self.handle(var)
        assert h.mode == '<'
        self.last = h
        at_end = h.ended or h.pos >= len(self.files[h.name])
        if at_end:
            h.ended = True
        self.say('eof\n' if at_end else 'more\n')

    def write(self, var, word, items, block=None, fmt=None):
        """`items` are strings and numbers; `fmt` a printf format."""
        to = f'{{{block or "$" + var}}}' if block is not None else f'${var}'
        written = ', '.join(quote(i) if isinstance(i, str) else str(i) for i in items)
        if word == 'printf':
            written = quote(fmt) + (', ' + written if written else '')
        self.emit(f'{word} {to} {written};')
        if self.status is not None:
            return
        h = self.handle(var)
        assert h.mode in ('>', '>>')
        if word == 'printf':
            text = fmt % tuple(items)
        else:
            text = ''.join(str(i) for i in items) + ('\n' if word == 'say' else '')
        self.files[h.name] += text.encode('utf-8' if self.utf8 else 'latin-1')

    def perl(self, text, printed=''):
        """A statement the model does not read, and what it prints."""
        self.emit(text)
        self.say(printed)

    # ---- stdin
    def stdin_one(self):
        t = self.fresh('s')
        self.emit(f'my ${t} = <STDIN>; say defined ${t} ? show(${t}) : "undef";')
        if self.status is not None:
            return
        self.last = 'STDIN'
        got = None
        if not self.stdin_ended:
            end = self.stdin.find(b'\n', self.stdin_pos)
            if end < 0:
                self.stdin_ended = True
                self.errno, self.failed = 0, False
                line, self.stdin_pos = self.stdin[self.stdin_pos:], len(self.stdin)
            else:
                line, self.stdin_pos = self.stdin[self.stdin_pos:end + 1], end + 1
            if line:
                self.stdin_lines += 1
                got = self.chars(line)
        self.say((self.shown(got) if got is not None else 'undef') + '\n')

    # ---- messages
    def message(self, text, at):
        if text.endswith('\n'):
            return text
        if self.last == 'STDIN' and self.stdin_lines:
            return f'{text} at {FILE.format(name=self.name)} line {at}, <STDIN> line {self.stdin_lines}.\n'
        assert not (isinstance(self.last, Handle) and self.last.lines), 'the model writes no message a fault would stop (D279)'
        return f'{text} at {FILE.format(name=self.name)} line {at}.\n'

    def warn(self, text):
        at = self.line()
        self.emit(f'warn {quote(text)};')
        if self.status is None:
            self.err += self.message(text, at)

    def die_now(self, text, at):
        self.err += self.message(text, at)
        self.status = self.errno if self.errno else 255

    def die(self, text):
        at = self.line()
        self.emit(f'die {quote(text)};')
        if self.status is None:
            self.die_now(text, at)

    def show_errno(self):
        """`$!`, which is read while the last open failed."""
        self.emit('say "[$!]";')
        if self.status is None:
            assert self.failed, 'the model reads $! only after an open that failed'
            self.say(f'[{os.strerror(self.errno)}]\n')

    # ---- the end
    def kind(self):
        status = self.status or 0
        return 'dies' if status == 255 else 'warns' if status or self.err else 'same'

    def program(self):
        self.kind_hint = None if self.kind() == 'same' else self.kind()
        return '\n'.join([*self.head(self.kind_hint), 'use v5.42;', *self.prelude, *self.body]) + '\n'

    def expected(self):
        return self.out + self.err + (f'exit: {self.status}\n' if self.status else '')


def world(n, **said):
    w = World(f'{n}-{NAMES[n]}', **said)
    w.number = n
    # Whether the program has a `# kind:` header moves every line by one:
    # a case says first what it will be.
    w.kind_hint = KINDS.get(n)
    return w


WORDS = ['a', 'bc', '0', 'x y', '', '42', ' ', 'q\tz', '-1', '0.5']


def text(rnd, n, last_newline=True):
    body = '\n'.join(rnd.choice(WORDS) for _ in range(n))
    return (body + ('\n' if last_newline else '')).encode()


# ---- the same tests

def case_lines(w, rnd):
    w.files.update({'full.txt': text(rnd, 4), 'cut.txt': text(rnd, 3, False), 'empty.txt': b'', 'one.txt': b'only\n', 'blank.txt': b'\n\n'})
    w.given = dict(w.files)
    for name in w.files:
        w.open('fh', '<', name, my=name == 'full.txt')
        for _ in range(7):
            if rnd.random() < 0.5:
                w.eof('fh')
            w.one('fh')
        w.eof('fh')
        w.close('fh')


def case_lists(w, rnd):
    w.files.update({'five.txt': text(rnd, 5), 'cut.txt': text(rnd, 4, False), 'empty.txt': b''})
    w.given = dict(w.files)
    w.perl('sub count(@lines) { return scalar(@lines) }')
    for how in ('array', 'split', 'for', 'call', 'while'):
        for name in w.files:
            w.open('fh', '<', name, my=False if w.vars else True)
            if rnd.random() < 0.5:
                w.one('fh')
            w.all('fh', how)
            w.all('fh', how)
            w.one('fh')
            w.close('fh')


def case_while(w, rnd):
    w.files.update({'zero.txt': b'a\n0', 'zeros.txt': b'0\n0\n\n0\n', 'blank.txt': b'\n', 'empty.txt': b'', 'space.txt': b' \n0.0\n00\n'})
    w.given = dict(w.files)
    for k, name in enumerate(w.files):
        var = f'in{k}'
        w.open(var, '<', name, how='or die')
        w.all(var, 'while')
        w.eof(var)
        w.close(var, 'bare')


def case_write(w, rnd):
    w.open('out', '>', 'made.txt', how='or die')
    w.write('out', 'print', ['first ', 1, '\n'])
    w.write('out', 'say', ['second', 2])
    w.write('out', 'printf', ['x', 7, 1.5], fmt='%s-%03d-%.2f\n')
    w.write('out', 'print', ['block\n'], block='$out')
    w.write('out', 'say', ['spaced'], block=' $out ')
    w.write('out', 'printf', [5], block='$out', fmt='%d%%\n')
    w.write('out', 'print', [0.5, ' ', -3, ' ', 1e21, '\n'])
    w.close('out', 'or die')
    w.open('in', '<', 'made.txt', how='or die')
    w.all('in', 'array')
    w.close('in')
    w.open('out', '>>', 'made.txt', my=False)
    w.write('out', 'print', ['added\n'])
    w.close('out')
    w.open('out', '>>', 'new.txt', my=False)
    w.write('out', 'print', ['no newline'])
    w.close('out')
    w.open('out', '>', 'none.txt', my=False)
    w.close('out')
    for name in ('made.txt', 'new.txt', 'none.txt'):
        w.open('in', '<', name, my=False)
        w.all('in', 'array')
        w.close('in')
    w.open('out', '>', 'made.txt', my=False)
    w.write('out', 'say', ['again'])
    w.close('out', 'value')
    w.open('in', '<', 'made.txt', my=False)
    w.all('in', 'array')
    w.close('in')
    # A heredoc after a handle, and a list worked out as it is written.
    w.open('out', '>', 'here.txt', my=False)
    w.perl('print $out <<"END";\nfrom a heredoc here\nEND')
    w.files['here.txt'] += b'from a heredoc here\n'
    w.perl('my @items = (1, 2, 3);')
    w.perl('print $out "@items", "\\n", scalar(@items), "\\n";')
    w.files['here.txt'] += b'1 2 3\n3\n'
    w.perl('say $out join("-", map { $_ * 2 } @items);')
    w.files['here.txt'] += b'2-4-6\n'
    w.perl('print $out !1, "|", !0, "\\n";')
    w.files['here.txt'] += b'|1\n'
    w.close('out')
    w.open('in', '<', 'here.txt', my=False)
    w.all('in', 'array')
    w.close('in')


def case_values(w, rnd):
    w.files.update({'abc.txt': b'a\nb\nc\nd\ne\nf\ng\n', 'xy.txt': b'x\ny\n'})
    w.given = dict(w.files)
    w.open('fh', '<', 'abc.txt', how='or die')
    h = w.handle('fh')

    def line(text):
        got = w.read(h)
        w.perl(text, w.shown(got) + '\n')
    w.perl('say ref($fh), " ", ref(\\$fh), " ", defined($fh) ? "defined" : "undef", " ", $fh ? "true" : "false";', 'GLOB REF defined true\n')
    w.perl('my $copy = $fh;')
    line('my $c1 = <$copy>; say show($c1);')
    w.perl('say $copy == $fh ? "one" : "two", " ", $copy != $fh ? "differ" : "same";', 'one same\n')
    w.perl('my %h = (in => $fh);')
    w.perl('my @a = ($fh);')
    w.perl('my $from = $h{in};')
    line('my $c2 = <$from>; say show($c2);')
    w.perl('sub next_of($h) { my $l = <$h>; return $l }')
    line('say show(next_of($a[0]));')
    w.perl('my $reader = sub { my $l = <$fh>; return $l };')
    line('say show($reader->());')
    w.perl('sub opened($name) { open(my $new, \'<\', $name) or die "no $name\\n"; return $new }')
    w.perl('my $other = opened("xy.txt");')
    w.perl('say $other == $fh ? "one" : "two", " ", $other != $fh ? "differ" : "same";', 'two differ\n')
    w.perl('my $o1 = <$other>; say show($o1);', w.shown('x\n') + '\n')
    w.perl('try { die $fh } catch ($e) { my $l = <$e>; say "caught ", ref($e), " ", show($l) }', '')
    got = w.read(h)
    w.say(f'caught GLOB {w.shown(got)}\n')
    w.perl('my $r = \\$fh; my $through = $r->$*;')
    line('my $c3 = <$through>; say show($c3);')
    # An open of the variable opens the same handle again: every copy sees it.
    w.perl("open($fh, '<', 'xy.txt') or die \"no\\n\";")
    w.perl('my $c4 = <$copy>; say show($c4);', w.shown('x\n') + '\n')
    w.perl('my $c5 = <$from>; say show($c5);', w.shown('y\n') + '\n')
    w.perl('say eof($a[0]) ? "eof" : "more", " ", $copy == $fh ? "one" : "two";', 'eof one\n')
    w.perl('close($copy);')
    w.perl("open($copy, '<', 'abc.txt') or die \"no\\n\";")
    w.perl('my $c6 = <$fh>; say show($c6);', w.shown('a\n') + '\n')
    w.perl('close($h{in});')
    w.perl('close($other);')
    w.perl('my @handles = map { opened($_) } "abc.txt", "xy.txt", "abc.txt";')
    w.perl('for my $each (@handles) { my $l = <$each>; print $l; close($each) }', 'a\nx\na\n')
    w.perl('my @globs = grep { ref($_) eq "GLOB" } @handles, 5, "GLOB", [1];')
    w.perl('say scalar(@globs);', '3\n')


def case_fails(w, rnd):
    w.files.update({'here.txt': b'h\n'})
    w.given = dict(w.files)
    w.open('h1', '<', 'nope.txt', how='if')
    w.open('h2', '<', 'here.txt', how='if')
    w.open('h3', '<', 'nope.txt', how='value')
    w.show_errno()
    w.perl('say ref($h3), " ", defined($h3) ? "defined" : "undef", " ", $h3 ? "true" : "false";', 'GLOB defined true\n')
    words = os.strerror(ENOENT)
    w.perl('say "e1: $!.";', f'e1: {words}.\n')
    w.perl('say "e2: " . $! . "!";', f'e2: {words}!\n')
    w.perl('say "e3: $!::x $!->";', f'e3: {words}::x {words}->\n')
    w.perl('my $why = $!; say length($why), " ", $why eq "' + words + '" ? "the words" : "others", " ", $! ? "true" : "false";', f'{len(words)} the words true\n')
    w.perl('my @whys = ($!, "$!");', '')
    w.perl('say scalar(@whys), " ", $whys[0] eq $whys[1] ? "same" : "differ";', '2 same\n')
    w.perl('unless (open(my $d, \'<\', "no/such/dir/x.txt")) { say "unless: $!" }', f'unless: {words}\n')
    w.perl('my $h5; my $r = open($h5, \'<\', \'nope.txt\'); say defined $r ? "defined" : "undef", " ", ref($h5);', 'undef GLOB\n')
    w.perl("open($h5, '<', 'here.txt') or die \"no\\n\"; my $l = <$h5>; print $l; close($h5);", 'h\n')
    w.errno, w.failed = ENOTTY, False
    w.open('w', '>', 'no/such/dir/x.txt')
    w.show_errno()
    w.open('ap', '>>', 'no/such/dir/x.txt', how='if', label='x.txt')
    w.show_errno()


def case_bytes(w, rnd):
    w.files.update({'bytes.txt': b'caf\xc3\xa9\n\xff\x80\n\x00 nul\n', 'crlf.txt': b'a\r\nb\r\n\rc', 'tabs.txt': b'\t\n \n'})
    w.given = dict(w.files)
    for name in w.files:
        w.open('fh', '<', name, my=not w.vars, how='or die')
        w.one('fh')
        w.all('fh', 'array')
        w.close('fh')


def case_utf8(w, rnd):
    w.files.update({'u.txt': 'café\n☺ and \U0001F600\n﻿bom'.encode('utf-8')})
    w.given = dict(w.files)
    w.open('fh', '<', 'u.txt', how='or die')
    w.all('fh', 'array')
    w.close('fh')
    w.open('out', '>', 'w.txt', how='or die')
    w.perl('print $out "é", chr(9786), "\\n";')
    w.files['w.txt'] += 'é☺\n'.encode('utf-8')
    w.perl('say $out chr(0x10FFFD), "ñ";')
    w.files['w.txt'] += '\U0010FFFDñ\n'.encode('utf-8')
    w.perl('printf $out "%s|%3s|\\n", "ü", "é";')
    w.files['w.txt'] += 'ü|  é|\n'.encode('utf-8')
    w.close('out')
    w.open('fh', '<', 'w.txt', my=False)
    w.all('fh', 'array')
    w.close('fh')
    w.open('fh', '<', 'w.txt', my=False)
    w.perl('my $first = <$fh>; print $first;', 'é☺\n')
    w.close('fh')


def case_dropped(w, rnd):
    w.perl('sub save($name, $text) { open(my $out, \'>\', $name) or die "no $name\\n"; print $out $text; }')
    w.perl('sub slurp($name) { open(my $in, \'<\', $name) or die "no $name\\n"; my @lines = <$in>; return join("", @lines); }')
    w.perl('save("kept.txt", "kept\\n");')
    w.perl('print slurp("kept.txt");', 'kept\n')
    w.perl('save("kept.txt", "again\\n");')
    w.perl('print slurp("kept.txt"), slurp("kept.txt");', 'again\nagain\n')
    w.perl('sub add($name, $text) { open(my $out, \'>>\', $name) or die "no $name\\n"; print $out $text; return; }')
    w.perl('for my $i (1 .. 5) { add("log.txt", "line $i\\n"); }')
    w.perl('print slurp("log.txt");', ''.join(f'line {i}\n' for i in range(1, 6)))
    w.perl('sub first_line($name) { open(my $in, \'<\', $name) or die "no $name\\n"; my $l = <$in>; return $l; }')
    w.perl('print first_line("log.txt");', 'line 1\n')
    w.perl('add("log.txt", "last\\n");')
    w.perl('my @all = (slurp("log.txt"));')
    w.perl('say length($all[0]);', '40\n')


def case_many(w, rnd):
    # More handles dropped than the system lets a program hold open: each
    # is closed when it is collected, and an open that finds no room left
    # collects first. (The stress knob is off, or every allocation would
    # collect.)
    w.files.update({'in.txt': b'a\nb\n'})
    w.given = dict(w.files)
    w.perl('my $read = "";')
    w.perl('for my $i (1 .. 1500) {')
    w.perl("    open(my $fh, '<', 'in.txt') or die \"open $i: $!\\n\";")
    w.perl('    my $l = <$fh>;')
    w.perl('    $read = $l if $i == 1500;')
    w.perl('}')
    w.perl('print $read;', 'a\n')
    w.perl('for my $i (1 .. 1500) {')
    w.perl("    open(my $out, '>>', 'out.txt') or die \"open $i: $!\\n\";")
    w.perl('    print $out "x";')
    w.perl('    close($out);')
    w.perl('}')
    w.perl("open(my $in, '<', 'out.txt') or die \"no\\n\";")
    w.perl('my $made = <$in>;')
    w.perl('say length($made);', '1500\n')


def case_stdin(w, rnd):
    w.files.update({'in.txt': b'f1\nf2\n', 'empty.txt': b''})
    w.given = dict(w.files)
    w.warn('before')
    w.stdin_one()
    w.warn('stdin read')
    w.open('fh', '<', 'empty.txt')
    w.warn('opened')
    w.one('fh')
    w.warn('nothing read from the file')
    w.stdin_one()
    w.warn('stdin again')
    w.open('in', '<', 'in.txt')
    w.one('in')
    w.close('in')
    w.warn('read and closed')
    w.perl('say eof(STDIN) ? "eof" : "more";', 'more\n')
    w.last = 'STDIN'
    w.warn('eof of stdin')
    w.open('in', '<', 'in.txt', my=False)
    w.eof('in')
    w.warn('eof of the file')
    w.stdin_one()
    w.stdin_one()
    w.warn('stdin at its end')
    w.perl('try { die "caught" } catch ($e) { print "c: $e" }', f'c: caught at {FILE.format(name=w.name)} line {w.line()}, <STDIN> line 3.\n')


def case_formats(w, rnd):
    w.open('out', '>', 'f.txt', how='or die')
    w.perl('sub report($to, $name, $n) { printf {$to} "%-6s|%4d|%5.1f|%x\\n", $name, $n, $n / 3, $n; return; }')
    for name, n in (('ab', 7), ('longer', 1234), ('', 0), ('q', 255)):
        w.perl(f'report($out, {quote(name)}, {n});')
        w.files['f.txt'] += ('%-6s|%4d|%5.1f|%x\n' % (name, n, n / 3, n)).encode()
    w.perl('my %to = (log => $out);')
    w.perl('say { $to{log} } "through a hash ", 1 + 1;')
    w.files['f.txt'] += b'through a hash 2\n'
    w.perl('my @outs = ($out);')
    w.perl('print { $outs[0] } "through an array\\n";')
    w.files['f.txt'] += b'through an array\n'
    w.perl('my $pick = 1;')
    w.perl('print { $pick ? $out : $outs[0] } "picked\\n";')
    w.files['f.txt'] += b'picked\n'
    w.perl('printf $out "%s\\n", "plain" if $pick;')
    w.files['f.txt'] += b'plain\n'
    w.perl('say $out "no" unless $pick;')
    w.perl('print $out "each $_\\n" for 1 .. 3;')
    w.files['f.txt'] += b'each 1\neach 2\neach 3\n'
    w.perl('sub last_value($to) { print $to "in a sub\\n" }')
    w.perl('say last_value($out) ? "true" : "false";', 'true\n')
    w.files['f.txt'] += b'in a sub\n'
    w.close('out')
    w.open('in', '<', 'f.txt', how='or die')
    w.perl('print <$in>;', w.files['f.txt'].decode())
    w.handle('in').pos = len(w.files['f.txt'])
    w.handle('in').ended = True
    w.eof('in')


def case_or_die(w, rnd):
    w.files.update({'in.txt': b'a\n'})
    w.given = dict(w.files)
    w.open('h1', '<', 'in.txt', how='or die')
    w.open('h2', '<', 'in.txt', how='|| die')
    w.open('h3', '<', 'in.txt', how='unless')
    w.open('h4', '<', 'in.txt', how='or die line')
    w.close('h1', 'or die')
    w.close('h2', 'bare')
    w.perl('close $h3 or die "cannot close: $!\\n";')
    w.handle('h3').mode = None
    w.perl('close($h4) || die "cannot close: $!\\n";')
    w.handle('h4').mode = None
    w.perl('my $ok = 1;')
    w.perl("open($h1, '<', 'in.txt') or die \"no\\n\" if $ok;")
    w.perl('close $h1 if $ok;')
    w.perl('say "all opened and closed";', 'all opened and closed\n')


SAME = {6400: case_lines, 6401: case_lists, 6402: case_while, 6403: case_write, 6404: case_values, 6405: case_fails,
        6406: case_bytes, 6407: case_utf8, 6408: case_dropped, 6409: case_many, 6410: case_stdin, 6411: case_formats,
        6412: case_or_die}
SAID = {6400: {'show': True}, 6401: {'show': True}, 6402: {'show': True}, 6403: {'show': True}, 6404: {'show': True},
        6406: {'show': True}, 6407: {'utf8': True, 'show': True}, 6409: {'env': 'CURLY_GC_STRESS=0 CURLY_GC_POISON=0'},
        6410: {'show': True, 'stdin': b's1\ns2\ns3'}}


# ---- what a program exits with (D272)

ABC = {'in.txt': b'a\nb\nc\n'}


def exit_open(w):
    w.open('fh', '<', 'in.txt')
    w.perl('say "opened";', 'opened\n')
    w.die('an open that worked leaves errno 25\n')


def exit_fail(w):
    w.perl('say "before";', 'before\n')
    w.open('fh', '<', 'nope.txt', how='or die line')
    w.perl('say "not reached";')


def exit_read_all(w):
    w.open('fh', '<', 'in.txt', how='or die')
    w.all('fh', 'while')
    w.die('the end was met\n')


def exit_read_some(w):
    w.open('fh', '<', 'in.txt', how='or die')
    w.one('fh')
    w.one('fh')
    w.one('fh')
    w.die('three lines, and the end not met\n')


def exit_eof(w):
    w.open('fh', '<', 'in.txt', how='or die')
    w.all('fh', 'while')
    w.open('fh', '<', 'in.txt', my=False)
    w.one('fh')
    w.one('fh')
    w.one('fh')
    w.eof('fh')
    w.one('fh')
    w.all('fh', 'array')
    w.die('eof met the end, and no read looked again\n')


def exit_list(w):
    w.open('fh', '<', 'in.txt', how='or die')
    w.open('other', '<', 'in.txt', how='or die')
    w.all('fh', 'array')
    w.die('a list met the end\n')


def exit_partial(w):
    w.open('fh', '<', 'cut.txt', how='or die')
    w.one('fh')
    w.open('other', '<', 'cut.txt', how='or die')
    w.one('fh')
    w.die('the last line has no newline: the end was met\n')


def exit_write(w):
    w.open('out', '>', 'o.txt', how='or die')
    w.write('out', 'print', ['written\n'])
    w.close('out')
    w.open('out', '>>', 'o.txt', my=False)
    w.die('written, closed, and opened again\n')


def exit_stdin(w):
    w.open('fh', '<', 'in.txt', how='or die')
    w.stdin_one()
    w.stdin_one()
    w.die('stdin met its end\n')


def exit_fail_ok_fail(w):
    w.open('h1', '<', 'nope.txt', how='if')
    w.open('h2', '<', 'in.txt', how='if')
    w.open('h3', '<', 'nope.txt', how='if')
    w.die('the last open failed\n')


def exit_closed(w):
    w.open('fh', '<', 'in.txt', how='or die')
    w.one('fh')
    w.close('fh')
    w.die('a line was read, and the handle closed')


def exit_caught(w):
    w.perl('sub slurp($name) { open(my $in, \'<\', $name) or die "no $name: $!\\n"; my @l = <$in>; close($in); return @l }')
    w.perl('try { slurp("nope.txt") } catch ($e) { print "caught: $e" }', f'caught: no nope.txt: {os.strerror(ENOENT)}\n')
    w.errno, w.failed = ENOENT, True
    w.die('after a caught one\n')


def exit_underflow(w):
    # A number that underflowed sets errno too (D151), and an open after
    # it sets it again.
    w.perl('my $tiny = "1e-400" + 0;')
    w.perl('say $tiny;', '0\n')
    w.open('fh', '<', 'in.txt', how='or die')
    w.die('the open set errno after the underflow did\n')


EXITS = {6420: (exit_open, ABC, None), 6421: (exit_fail, {}, None), 6422: (exit_read_all, ABC, None), 6423: (exit_read_some, ABC, None),
         6424: (exit_eof, ABC, None), 6425: (exit_list, ABC, None), 6426: (exit_partial, {'cut.txt': b'x\ny'}, None),
         6427: (exit_write, {}, None), 6428: (exit_stdin, ABC, b'only'), 6429: (exit_fail_ok_fail, ABC, None),
         6430: (exit_closed, ABC, None), 6431: (exit_caught, {}, None), 6432: (exit_underflow, ABC, None)}
# What each will be, which the count of its lines needs before it is run.
KINDS = {6410: 'warns', 6420: 'warns', 6421: 'warns', 6422: 'dies', 6423: 'warns', 6424: 'warns', 6425: 'dies', 6426: 'dies',
         6427: 'warns', 6428: 'dies', 6429: 'warns', 6430: 'warns', 6431: 'warns', 6432: 'warns'}


# ---- the faults: the program, what it printed first, the message, the line

UTF8 = ['use utf8;', "use open ':std', ':encoding(UTF-8)';"]
CLOSED = 'a file handle that is not open'
READING = 'a file handle opened for reading'
WRITING = 'a file handle opened for writing'
TWICE = 'open of a file the program has open, one of the two for writing'
PAST = "$! where no open has just failed"
MESSAGE = 'a die or a warn with no newline at its end while a file a line was read from is open'
REF_STR = 'a reference where a string is wanted'
IN = "open(my $fh, '<', 'in.txt') or die \"no\\n\";"
OUT = "open(my $out, '>', 'o.txt') or die \"no\\n\";"

# number: (name, files, prelude, body, printed, message, line of the body)
FAULTS = {
    6440: ('close-twice', ABC, [], [IN, 'close($fh);', 'say "closed";', 'close($fh);', 'say "not reached";'], 'closed\n', f'close of {CLOSED}', 4),
    6441: ('close-never-opened', {}, [], ["open(my $fh, '<', 'nope.txt');", 'say "before";', 'close($fh);'], 'before\n', f'close of {CLOSED}', 3),
    6442: ('read-closed', ABC, [], [IN, 'my $l = <$fh>;', 'print $l;', 'close($fh);', '$l = <$fh>;', 'say "not reached";'], 'a\n', f'read of {CLOSED}', 5),
    6443: ('read-list-closed', ABC, [], [IN, 'close($fh);', 'say "before";', 'my @l = <$fh>;'], 'before\n', f'read of {CLOSED}', 4),
    6444: ('read-after-failed-open', {}, [], ["open(my $fh, '<', 'nope.txt');", 'say "before";', 'my $l = <$fh>;'], 'before\n', f'read of {CLOSED}', 3),
    6445: ('read-write-only', {}, [], [OUT, 'say "before";', 'my $l = <$out>;'], 'before\n', f'read of {WRITING}', 3),
    6446: ('read-append-only', {}, [], ["open(my $out, '>>', 'o.txt') or die \"no\\n\";", 'say "before";', 'my @l = <$out>;'], 'before\n', f'read of {WRITING}', 3),
    6447: ('write-closed', {}, [], [OUT, 'print $out "x";', 'close($out);', 'say "before";', 'print $out "y";'], 'before\n', f'write to {CLOSED}', 5),
    6448: ('say-closed', {}, [], [OUT, 'close($out);', 'say "before";', 'say {$out} "y";'], 'before\n', f'write to {CLOSED}', 4),
    6449: ('printf-closed', {}, [], [OUT, 'close($out);', 'say "before";', 'printf $out "%s", "y";'], 'before\n', f'write to {CLOSED}', 4),
    6450: ('write-read-only', ABC, [], [IN, 'say "before";', 'print $fh "x";'], 'before\n', f'write to {READING}', 3),
    6451: ('say-read-only', ABC, [], [IN, 'say "before";', 'say $fh "x";'], 'before\n', f'write to {READING}', 3),
    6452: ('printf-read-only', ABC, [], [IN, 'say "before";', 'printf {$fh} "%d", 1;'], 'before\n', f'write to {READING}', 3),
    6453: ('eof-closed', ABC, [], [IN, 'say eof($fh) ? "eof" : "more";', 'close($fh);', 'say eof($fh) ? "eof" : "more";'], 'more\n', f'eof of {CLOSED}', 4),
    6454: ('eof-write-only', {}, [], [OUT, 'say "before";', 'say eof($out) ? "eof" : "more";'], 'before\n', f'eof of {WRITING}', 3),
    6455: ('twice-write-then-read', {}, [], [OUT, 'print $out "x\\n";', 'say "before";', "open(my $in, '<', 'o.txt');", 'say "not reached";'], 'before\n', TWICE, 4),
    6456: ('twice-read-then-write', ABC, [], [IN, 'say "before";', "open(my $out, '>', 'in.txt');", 'say "not reached";'], 'before\n', TWICE, 3),
    6457: ('twice-write-write', {}, [], [OUT, 'say "before";', "open(my $more, '>>', 'o.txt');"], 'before\n', TWICE, 3),
    6458: ('twice-read-then-append', ABC, [], [IN, 'my $copy = $fh;', 'say "before";', "open(my $out, '>>', './in.txt');"], 'before\n', TWICE, 4),
    6459: ('open-directory', {}, [], ['say "before";', "open(my $d, '<', '.');", 'say "not reached";'], 'before\n', 'open of what is not a plain file', 2),
    6460: ('open-name-nul', ABC, [], ['say "before";', 'my $name = "in.txt\\0x";', "open(my $fh, '<', $name);"], 'before\n', "a NUL in a file's name", 3),
    6461: ('open-name-past-ascii', {}, ['use utf8;'], ['say "before";', "open(my $fh, '>', 'café.txt');"], 'before\n', "a character past ASCII in a file's name", 2),
    6462: ('open-name-undef', {}, [], ['my $name;', 'say "before";', "open(my $fh, '<', $name);"], 'before\n', 'undef where a string is wanted', 3),
    6463: ('open-name-reference', {}, [], ['my $name = ["in.txt"];', 'say "before";', "open(my $fh, '<', $name);"], 'before\n', REF_STR, 3),
    6464: ('open-variable-number', ABC, [], ['my $fh = 5;', 'say "before";', "open($fh, '<', 'in.txt');", 'say "not reached";'], 'before\n', "open's variable holds what is not a file handle", 3),
    6465: ('open-variable-reference', ABC, [], ['my $fh = [1];', 'say "before";', "open($fh, '<', 'in.txt');"], 'before\n', "open's variable holds what is not a file handle", 3),
    6466: ('errno-no-open', {}, [], ['say "before";', 'say "[$!]";'], 'before\n', PAST, 2),
    6467: ('errno-after-success', ABC, [], ["open(my $no, '<', 'nope.txt');", 'say length($!) > 0 ? "words" : "none";', IN, 'say "why: " . $!;'], 'words\n', PAST, 4),
    6468: ('errno-after-end', ABC, [], ["open(my $fh, '<', 'in.txt');", "open(my $no, '<', 'nope.txt');", 'my @l = <$fh>;', 'say scalar(@l);', 'my $why = $!;'], '3\n', PAST, 5),
    6469: ('errno-after-stdin-end', {}, [], ["open(my $no, '<', 'nope.txt');", 'my $l = <STDIN>;', 'say defined $l ? "line" : "undef";', 'say $!;'], 'undef\n', PAST, 4),
    6470: ('errno-as-number', {}, [], ["open(my $no, '<', 'nope.txt');", 'say "before";', 'my $n = $! + 0;'], 'before\n', 'not a numeric string', 3),
    6471: ('message-warn', ABC, [], [IN, 'my $l = <$fh>;', 'print $l;', 'warn "careful";', 'say "not reached";'], 'a\n', MESSAGE, 4),
    6472: ('message-die', ABC, [], [IN, 'while (my $l = <$fh>) {', '    print $l;', '    die "bad line" if $l eq "b\\n";', '}'], 'a\nb\n', MESSAGE, 4),
    6473: ('message-die-caught', ABC, [], [IN, 'my @l = <$fh>;', 'say scalar(@l);', 'try { die "inside" } catch ($e) { say "not reached" }'], '3\n', MESSAGE, 4),
    6474: ('message-after-eof', ABC, [], [IN, 'my $l = <$fh>;', "open(my $other, '<', 'in.txt');", 'my $s = <STDIN>;', 'say eof($fh) ? "eof" : "more";', 'warn "w";'], 'more\n', MESSAGE, 6),
    6475: ('message-or-die', ABC, [], [IN, 'my $l = <$fh>;', 'say "before";', "open(my $no, '<', 'nope.txt') or die \"cannot open nope.txt: $!\";"], 'before\n', MESSAGE, 4),
    6476: ('message-opened-again', ABC, [], [IN, 'my $l = <$fh>;', "open($fh, '<', 'in.txt');", 'say "before";', 'warn "the count of lines goes on";'], 'before\n', MESSAGE, 5),
    6477: ('handle-printed', ABC, [], [IN, 'say "before";', 'print $fh;'], 'before\n', REF_STR, 3),
    6478: ('handle-printed-comma', ABC, [], [IN, 'say "before";', 'print $fh, "x";'], 'before\n', REF_STR, 3),
    6479: ('handle-in-a-string', ABC, [], [IN, 'say "before";', 'my $s = "to $fh";'], 'before\n', REF_STR, 3),
    6480: ('handle-as-number', ABC, [], [IN, 'say "before";', 'my $n = $fh + 1;'], 'before\n', 'a reference where a number is wanted', 3),
    6481: ('handle-as-key', ABC, [], [IN, 'say "before";', 'my %h = ($fh => 1);'], 'before\n', REF_STR, 3),
    6482: ('handle-compared', ABC, [], [IN, 'say "before";', 'say $fh == 5 ? "five" : "other";'], 'before\n', 'a reference where a number is wanted', 3),
    6483: ('not-a-handle-print', {}, [], ['my $x = 5;', 'say "before";', 'print $x "text";', 'say "not reached";'], 'before\n', 'not a file handle', 3),
    6484: ('not-a-handle-read', {}, [], ['my $x = "in.txt";', 'say "before";', 'my $l = <$x>;'], 'before\n', 'not a file handle', 3),
    6485: ('undef-handle-read', {}, [], ['my $u;', 'say "before";', 'my $l = <$u>;'], 'before\n', 'undef where a file handle is wanted', 3),
    6486: ('undef-handle-close', {}, [], ['my $u;', 'say "before";', 'close($u);'], 'before\n', 'undef where a file handle is wanted', 3),
    6487: ('not-a-handle-block', {}, [], ['my %h = (out => [1]);', 'say "before";', 'print { $h{out} } "text";'], 'before\n', 'not a file handle', 3),
    6488: ('write-past-ascii', {}, ['use utf8;'], [OUT, 'print $out "plain\\n";', 'say "before";', 'print $out "café\\n";', 'say "not reached";'], 'before\n', "a character past ASCII printed without 'use open'", 4),
    6489: ('write-noncharacter', {}, UTF8, [OUT, 'print $out "é\\n";', 'say "before";', 'print $out chr(0xFFFE);'], 'before\n', 'a noncharacter printed', 4),
    6490: ('read-malformed', {'bad.txt': b'ok\nx\xe9y\n'}, UTF8, ["open(my $fh, '<', 'bad.txt') or die \"no\\n\";", 'my $l = <$fh>;', 'print $l;', '$l = <$fh>;'], 'ok\n', 'malformed UTF-8 read', 4),
    6491: ('read-cut', {'cut.txt': b'ok\na\xc3'}, UTF8, ["open(my $fh, '<', 'cut.txt') or die \"no\\n\";", 'my @l = <$fh>;'], '', 'malformed UTF-8 read', 2),
    6492: ('read-past-ascii-printed', {'u.txt': b'caf\xc3\xa9\n'}, [], ["open(my $fh, '<', 'u.txt') or die \"no\\n\";", 'my $l = <$fh>;', 'say length($l);', 'print $l;'], '6\n', "a character past ASCII printed without 'use open'", 4),
    6493: ('printf-count', {}, [], [OUT, 'say "before";', 'printf $out "%s %s\\n", "one";'], 'before\n', 'missing argument in printf', 3),
    6494: ('write-undef', {}, [], [OUT, 'my $u;', 'say "before";', 'print $out "a", $u;'], 'before\n', 'undef where a string is wanted', 4),
    6495: ('handle-as-array', ABC, [], [IN, 'say "before";', 'my @l = $fh->@*;'], 'before\n', 'not a reference to an array', 3),
    6496: ('errno-after-underflow', {}, [], ["open(my $no, '<', 'nope.txt');", 'my $tiny = "1e-400" + 0;', 'say $tiny;', 'say $!;'], '0\n', PAST, 4),
    6497: ('eof-not-a-handle', {}, [], ['my $x = 0;', 'say "before";', 'say eof($x) ? "eof" : "more";'], 'before\n', 'not a file handle', 3),
    6498: ('message-warn-in-a-sub', ABC, [], ['sub note($text) { warn $text; return; }', IN, 'my $l = <$fh>;', 'say "before";', 'note("careful");'], 'before\n', MESSAGE, 1),
    6499: ('close-after-reopen-failed', ABC, [], [IN, "open($fh, '<', 'nope.txt');", 'say "before";', 'close($fh);'], 'before\n', f'close of {CLOSED}', 4),
}

NAMES = {6400: 'file-lines', 6401: 'file-lists', 6402: 'file-while', 6403: 'file-write', 6404: 'file-handles-as-values',
         6405: 'file-open-fails', 6406: 'file-bytes', 6407: 'file-utf8', 6408: 'file-dropped-handles', 6409: 'file-many-handles',
         6410: 'file-and-stdin', 6411: 'file-formats', 6412: 'file-or-die',
         6420: 'exit-open-worked', 6421: 'exit-open-failed', 6422: 'exit-read-to-the-end', 6423: 'exit-read-some',
         6424: 'exit-eof-met-the-end', 6425: 'exit-list-to-the-end', 6426: 'exit-last-line-cut', 6427: 'exit-written',
         6428: 'exit-stdin-to-the-end', 6429: 'exit-fail-ok-fail', 6430: 'exit-closed-no-newline', 6431: 'exit-after-caught',
         6432: 'exit-open-after-underflow'}
NAMES.update({n: 'fault-file-' + f[0] for n, f in FAULTS.items()})


def commands():
    out = []
    for n in sorted(NAMES):
        out.append(f'    python3 t/models/file.py --program {n} > t/{n}-{NAMES[n]}.pl')
        out.append(f'    python3 t/models/file.py {n} > t/{n}-{NAMES[n]}.expected')
    return '\n'.join(out)


def main(argv):
    if argv[0] == '--commands':
        print(commands())
        return
    want_program = argv[0] == '--program'
    n = int(argv[-1])
    rnd = random.Random(n)
    if n in SAME:
        w = world(n, **SAID.get(n, {}))
        SAME[n](w, rnd)
    elif n in EXITS:
        case, files, stdin = EXITS[n]
        w = world(n, files=files, stdin=stdin, show=n in (6422, 6423, 6424, 6425, 6426, 6428, 6430))
        case(w)
    else:
        name, files, prelude, body, printed, message, line = FAULTS[n]
        head = [f'# t/models/file.py {n}', '# kind: fault'] + (['# stdin: '] if False else []) + [f'# file: {k}={escape(v)}' for k, v in files.items()]
        if want_program:
            sys.stdout.write('\n'.join([*head, 'use v5.42;', *prelude, *body]) + '\n')
        else:
            at = len(head) + 1 + len(prelude) + line
            sys.stdout.write(f'{printed}fault: {message} at {FILE.format(name=f"{n}-{NAMES[n]}")} line {at}.\nexit: 1\n')
        return
    assert KINDS.get(n, 'same') == w.kind(), f'{n} is {w.kind()}, and KINDS says {KINDS.get(n, "same")}'
    sys.stdout.write(w.program() if want_program else w.expected())


if __name__ == '__main__':
    main(sys.argv[1:])
