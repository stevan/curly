#!/bin/sh
# Build perl 5.42.0 with Stevan's roles into PREFIX (default
# /opt/perl-5.42-roles): the referee for a program with a role in it
# (D181, D186). README.md says what the patch is and where it came from.
#
#   tools/perl-roles/build.sh [PREFIX]
#
# TARBALL, if set, is a perl-5.42.0.tar.gz already on disk; otherwise it
# is fetched from cpan.org. Either way its checksum is checked.
set -eu

PREFIX=${1:-/opt/perl-5.42-roles}
HERE=$(cd "$(dirname "$0")" && pwd)
SHA=e093ef184d7f9a1b9797e2465296f55510adb6dab8842b0c3ed53329663096dc

if command -v nproc >/dev/null 2>&1; then JOBS=$(nproc); else JOBS=$(sysctl -n hw.ncpu); fi
if command -v sha256sum >/dev/null 2>&1; then SUM="sha256sum"; else SUM="shasum -a 256"; fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"

if [ -n "${TARBALL:-}" ]; then
    cp "$TARBALL" perl-5.42.0.tar.gz
else
    curl -fsSLO https://www.cpan.org/src/5.0/perl-5.42.0.tar.gz
fi
echo "$SHA  perl-5.42.0.tar.gz" | $SUM -c -
tar xzf perl-5.42.0.tar.gz
cd perl-5.42.0

patch -p1 -s < "$HERE/roles-5.42.0.patch"

./Configure -des -Dprefix="$PREFIX" -Dman1dir=none -Dman3dir=none
make -j"$JOBS"
make install

# A plain 5.42.0 under this name would referee roles as syntax errors.
got=$("$PREFIX/bin/perl" -e 'use v5.42; use experimental "class";
    role R { method m { "roles" } } class C :does(R) { }
    print C->new->m, (C->new does R) ? " does\n" : " no\n"') || got=""
if [ "$got" != "roles does" ]; then
    echo "build.sh: $PREFIX/bin/perl has no roles (it printed '$got')" >&2
    exit 1
fi
echo "build.sh: $PREFIX/bin/perl has roles"
