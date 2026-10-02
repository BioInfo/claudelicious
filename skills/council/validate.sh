#!/usr/bin/env bash
# Validate the council skill: structure, lens schema, slate references.
set -uo pipefail

cd "$(dirname "$0")" || exit 1
fail=0
err() { echo "FAIL: $*"; fail=1; }
ok()  { echo "  ok: $*"; }

echo "== council skill validation =="

# 1. core files
for f in SKILL.md slates.md; do
  [[ -f "$f" ]] && ok "$f present" || err "$f missing"
done

# 2. lens roster
people=(munger bezos thiel taleb nietzsche)
ideas=(loonshots jobs-to-be-done second-order-effects base-rates pre-mortem leverage-points)
roles=(skeptic builder user-advocate infra-realist)

check_lens() {
  local path="$1" name="$2"
  if [[ ! -f "$path" ]]; then err "lens missing: $path"; return; fi
  # required frontmatter fields — the two that make it a decision tool
  for field in "name:" "library:" "scoring_axis:" "blind_to:"; do
    grep -q "^$field" "$path" || err "$name: missing frontmatter '$field'"
  done
  # name in frontmatter must match filename
  grep -q "^name: $name$" "$path" || err "$name: frontmatter name mismatch"
  # must declare its output contract
  grep -q "^Output:" "$path" || err "$name: no output contract"
  ok "lens $name"
}

for n in "${people[@]}"; do check_lens "lenses/thinkers/people/$n.md" "$n"; done
for n in "${ideas[@]}";  do check_lens "lenses/thinkers/ideas/$n.md"  "$n"; done
for n in "${roles[@]}";  do check_lens "lenses/roles/$n.md"          "$n"; done

# 2b. composition + orthogonality constraints declared in the roles lenses
grep -qi "jobs-to-be-done" lenses/roles/user-advocate.md || err "user-advocate: must declare orthogonality to jobs-to-be-done"
grep -q "^composes_with: red-team" lenses/roles/skeptic.md || err "skeptic: missing 'composes_with: red-team' (must defer to red-team for drafts)"

# 3. every seat named in a slate must have a lens file (any library)
echo "== slate cross-reference =="
seats_in_slates=$(grep -oE '\b(munger|bezos|thiel|taleb|nietzsche|loonshots|jobs-to-be-done|second-order-effects|base-rates|pre-mortem|skeptic|builder|user-advocate|infra-realist)\b' slates.md | sort -u)
for s in $seats_in_slates; do
  if [[ -f "lenses/thinkers/people/$s.md" || -f "lenses/thinkers/ideas/$s.md" || -f "lenses/roles/$s.md" ]]; then
    ok "slate seat '$s' resolves"
  else
    err "slate references unknown seat '$s'"
  fi
done

# 4. SKILL.md frontmatter pins a model (judgment skill → opus, per subagent-models.md)
grep -q "^model: opus$" SKILL.md || err "SKILL.md must pin 'model: opus' (synthesis is Opus judgment)"

# 5. orthogonality smoke check: munger (person) and a standalone inversion idea must not co-exist
[[ -f "lenses/thinkers/ideas/inversion.md" ]] && err "orthogonality: inversion idea-lens duplicates munger — remove one"

echo
if [[ $fail -eq 0 ]]; then echo "PASS — council skill valid"; else echo "VALIDATION FAILED"; fi
exit $fail
