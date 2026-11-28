# Names of files: every name is inside the run's own directory when a file is written.
def fo(mode, name, var='$o', my=True):
    return f"if (!open({'my ' if my else ''}{var}, '{mode}', {name})) {{ print \"fail: $!\\n\"; }}\n"
CASES = []
names = ["'d/o.txt'", "''", "'in.txt/'", "'in.txt/x'", '"a\\nb"', "'.'", "'..'", "'in.txt '", "' in.txt'", "'<in.txt'", "'in.txt|'", "'-'", "'sub'", "'sub/'", "'sub/f.txt'", "'sub/../in.txt'", "'.//in.txt'", "'x' x 300", "'x' x 5000", "'&STDIN'", "'&=0'", "'>x'", "'| cat'", "'in.txt\\0'", "undef", "5", "1.5", "true", "false", "[1]", '"in.txt"', "'IN.TXT'", "'~'", "'*'", "'in.*'"]
ronly = ["'/'", "'/dev/null'", "'/nonexistent/x'", "'/etc/hostname'", "'/proc/self/status'", "'/tmp'", "'//etc/hostname'"]
for n in names + ronly:
    for m in ('<', '>', '>>') if n in names else ('<',):
        CASES.append({'p': fo(m, n) + 'say "end";\n', 'files': {'sub/f.txt': b'sf\n'}})
        CASES.append({'p': f"open(my $o, '{m}', {n}) or die \"no: $!\\n\";\nsay \"end\";\n", 'files': {'sub/f.txt': b'sf\n'}})
        CASES.append({'p': f"open(my $o, '{m}', {n}) or die \"no: $!\";\nsay \"end\";\n", 'files': {'sub/f.txt': b'sf\n'}})
        CASES.append({'p': f"open(my $o, '{m}', {n});\ndie \"x\\n\";\n", 'files': {'sub/f.txt': b'sf\n'}})
        CASES.append({'p': f"open(my $o, '{m}', {n});\nif ('{m}' eq '<') {{ my @l = <$o>; print scalar(@l); }} else {{ print $o \"w\\n\"; }} close($o); say 'end';\n", 'files': {'sub/f.txt': b'sf\n'}})
