use v5.42;
END { print   "16.   So this is the end of the tale.\n" }
INIT { print  " 7. INIT blocks run FIFO just before runtime.\n" }
UNITCHECK {
  print       " 4.   And therefore before any CHECK blocks.\n"
}
CHECK { print " 6.   So this is the sixth line.\n" }
