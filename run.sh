#!/bin/sh
# run.sh NAME  (reads program from stdin), prints stdout, stderr, exit
P=/opt/perl-5.42/bin/perl
f=$1.pl; cat > $f
rm -f out*.txt
printf 'a\nb\nc\n' > in.txt; printf '' > empty.txt; printf 'x\ny' > nonl.txt
echo "== $1"; $P $f; echo "[exit $?]"
