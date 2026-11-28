use v5.42;
print "match: <$&>\n" while 'foo' =~ m{ o? }xg;
