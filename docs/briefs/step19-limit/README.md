# Step 19, the step limit: the evidence

2026-11-28. The independent review of step 19 (`../step19-review/`)
left one note for Stevan with nothing changed: the matcher's limit of
ten million steps was met by plain patterns on plain strings (T568).
`docs/PLAN.md`, step 19, "The step limit, a proposal" and "The step
limit, as built", have what was weighed and done (D240 to D244); this
directory has what it stands on.

- **`measure.py`**: the time and most resident memory of one match by
  the length of its subject, 10 KB to 10 MB, under this tree, under
  another tree's compiler, under the tests' knobs, with
  `CURLY_RE_PLAIN=1`, and under perl.
- **`onoff.py`**: the matcher with what D240 to D242 gave it held to
  the matcher without (`CURLY_RE_PLAIN=1`, the same binary), over the
  review's generator of patterns and subjects, its long subjects with
  them. No perl is asked: none of the three may change an answer,
  whatever the answer is.
- **`refusals.py`**: the table the refusal tests 5512 to 5515 are
  written from, by hand (T571).
- **`outputs.txt`**: what the runs recorded in `PLAN.md` printed.

Against perl the matcher is held by `../step19-review/differential.py`,
which since D240 gives three patterns in ten two subjects of 300 to
5,000 characters, and by `t/models/rematch.py`'s 5104. The breakages
are in `../step19-mutations.py`, named `limit:`.
