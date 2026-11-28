use v5.42;
$_ = <<'EOL';
    $url = URI::URL->new( "http://example.com/" );
    die if $url eq "xXx";
EOL

LOOP: {
    print(" digits"),       redo LOOP if /\G\d+\b[,.;]?\s*/gc;
    print(" lowercase"),    redo LOOP
                                  if /\G\p{Ll}+\b[,.;]?\s*/gc;
    print(" UPPERCASE"),    redo LOOP
                                  if /\G\p{Lu}+\b[,.;]?\s*/gc;
    print(" Capitalized"),  redo LOOP
                            if /\G\p{Lu}\p{Ll}+\b[,.;]?\s*/gc;
    print(" MiXeD"),        redo LOOP
                                     if /\G\pL+\b[,.;]?\s*/gc;
    print(" alphanumeric"), redo LOOP
                          if /\G[\p{Alpha}\pN]+\b[,.;]?\s*/gc;
    print(" line-noise"),   redo LOOP if /\G\W+/gc;
    print ". That's all!\n";
}
