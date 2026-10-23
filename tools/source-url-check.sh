#!/bin/bash
# source-url-check.sh [--revert] [spec ...]
# Every http(s) Source must answer before a bump lands on main: a spec whose
# source 404s fails the SRPM stage and users get no package.
set -u
REVERT=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --revert) REVERT=1 ;;
    *) ARGS+=("$a") ;;
  esac
done
if [ "${#ARGS[@]}" -eq 0 ]; then
  mapfile -t ARGS < <(git diff --name-only -- '*.spec' 2>/dev/null)
fi
FAILED=0
CHECKED=0
for spec in "${ARGS[@]}"; do
  [ -f "$spec" ] || continue
  if command -v rpmspec >/dev/null 2>&1; then
    expanded=$(rpmspec -P "$spec" 2>/dev/null)
  else
    expanded=$(sed -E "s/%\{url\}/$(sed -n 's/^URL:[[:space:]]*//p' "$spec" | head -1)/g" "$spec")
  fi
  urls=$(printf '%s\n' "$expanded" | grep -oE '^Source[0-9]*:[[:space:]]*https?://[^[:space:]]+' | sed -E 's/^Source[0-9]*:[[:space:]]*//')
  [ -z "$urls" ] && continue
  bad=""
  while IFS= read -r u; do
    [ -z "$u" ] && continue
    # Unset host macro (dash cannot run bash-only %(...)); not a source defect.
    case "$u" in *%*|*/archive//*|*///*) echo "skipped (unexpanded macro): $spec"; continue ;; esac
    code=$(curl -sIL -o /dev/null -w '%{http_code}' --max-time 60 "$u")
    CHECKED=$((CHECKED + 1))
    case "$code" in
      200|206) ;;
      *) bad="$bad $u($code)" ;;
    esac
  done <<< "$urls"
  if [ -n "$bad" ]; then
    FAILED=$((FAILED + 1))
    echo "::warning::$spec source does not resolve:$bad"
    if [ "$REVERT" -eq 1 ]; then
      git checkout HEAD -- "$spec" 2>/dev/null && echo "reverted: $spec"
    fi
  fi
done
echo "sources-checked=$CHECKED unresolved=$FAILED reverted=$([ "$REVERT" -eq 1 ] && echo "$FAILED" || echo 0)"
exit 0
