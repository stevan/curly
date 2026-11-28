use v5.42;
BEGIN { print " 1. BEGIN blocks run FIFO during compilation.\n" }
END { print   "15.   Read perlmod for the rest of the story.\n" }
CHECK { print " 5. CHECK blocks run LIFO after all compilation.\n" }
INIT { print  " 8.   Run this again, using Perl's -c switch.\n" }
