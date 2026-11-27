use v5.42;
printf "%2\$d %d\n",      12, 34;     # will print "34 12\n"
printf "%2\$d %d %d\n",   12, 34;     # will print "34 12 34\n"
printf "%3\$d %d %d\n",   12, 34, 56; # will print "56 12 34\n"
printf "%2\$*3\$d %d\n",  12, 34,  3; # will print " 34 12\n"
printf "%*1\$.*f\n",       4,  5, 10; # will print "5.0000\n"
