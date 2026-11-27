use v5.42;
"abc"=~/(.)(.)(.)/
    and print "Second buffer is ${^CAPTURE[1]}";
