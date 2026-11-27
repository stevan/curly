# uc, lc, ucfirst and lcfirst past ASCII, by perl's own tables (D257).
use v5.42;
use utf8;
use open ":std", ":encoding(UTF-8)";
say uc("é"), lc("É"), uc("ß"), ucfirst("ß"), lc("İ"), length lc("İ");
say ucfirst("ǆx"), uc("ǆ"), uc("ŉ"), uc("ﬃ"), lcfirst("ÉCOLE"), uc("straße");
say lc("ΑΣ"), uc("ω"), lc("Ω"), uc("ǰ"), ucfirst("ǳ"), lcfirst("Ǳ");
say uc("ÿ"), lc("Ÿ"), uc("ı"), lc("K"), uc("ꞵ"), lc(chr(0x10400)) eq chr(0x10428) ? "deseret" : "no";
say "\Uéa\E \uéa \Lǅ\E", ucfirst(""), uc(1.5);
