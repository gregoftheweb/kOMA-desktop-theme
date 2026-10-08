#!/usr/bin/env bash
# Omarchy-style windows without title bars, live: a KWin window rule that forces
# "No titlebar and frame" on normal windows. Unlike a newly installed decoration,
# which KWin only finds after the next sign-in, a rule applies as soon as KWin
# reloads its configuration. The focus border effect draws the outline.
# Keeps the user's own rules; safe to re-run. Needs kreadconfig6, kwriteconfig6.
set -euo pipefail

file=kwinrulesrc
rule=koma-no-titlebar

set_key() { kwriteconfig6 --file "$file" --group "$rule" --key "$1" "$2"; }
set_key Description "kOMA: no title bars"
set_key noborder true
set_key noborderrule 2 # 2 = force
set_key types 1        # normal windows only, not dialogs or panels
set_key wmclassmatch 0 # any application

rules=$(kreadconfig6 --file "$file" --group General --key rules)
case ",$rules," in
  *",$rule,"*) ;;
  *) rules="${rules:+$rules,}$rule" ;;
esac
kwriteconfig6 --file "$file" --group General --key rules "$rules"
IFS=, read -ra list <<<"$rules"
kwriteconfig6 --file "$file" --group General --key count "${#list[@]}"

if command -v qdbus6 >/dev/null; then
  qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
fi
echo "Title bars off (KWin rule $rule)"
