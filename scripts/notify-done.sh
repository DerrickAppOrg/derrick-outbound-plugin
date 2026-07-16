#!/usr/bin/env bash
# Signale la fin d'une phase longue (enrichissement) : cloche + notif desktop.
# Usage : notify-done.sh [nb_leads] [phase]
#   notify-done.sh 47 enrich
# Silencieux : DERRICK_NOTIFY=0. Voix macOS en plus : DERRICK_NOTIFY_VOICE=1.
set -uo pipefail

[ "${DERRICK_NOTIFY:-1}" = "0" ] && exit 0

N="${1:-}"
PHASE="${2:-enrich}"
LEADS="${N:+$N leads}"
LEADS="${LEADS:-Les leads}"

# Le derrick = la tour de forage. Le jeu de mot s'écrit tout seul.
case $((RANDOM % 5)) in
  0) MSG="Forage terminé. $LEADS remontés à la surface." ;;
  1) MSG="Le puits a donné : $LEADS enrichis. Vous pouvez reposer le café." ;;
  2) MSG="Derrick a fini de creuser. $LEADS frais sur le bureau." ;;
  3) MSG="Pause café terminée : $LEADS enrichis vous attendent." ;;
  4) MSG="Le derrick s'arrête. $LEADS, data fraîche du jour." ;;
esac

[ "$PHASE" != "enrich" ] && MSG="Phase $PHASE terminée. $MSG"

# La cloche terminal : le seul truc qui marche partout.
printf '\a'

case "$(uname -s)" in
  Darwin)
    afplay /System/Library/Sounds/Glass.aiff >/dev/null 2>&1 &
    osascript -e "display notification \"${MSG//\"/\\\"}\" with title \"Derrick\" subtitle \"Enrichissement terminé\"" >/dev/null 2>&1
    [ "${DERRICK_NOTIFY_VOICE:-0}" = "1" ] && say -v Thomas "Le forage est terminé" >/dev/null 2>&1 &
    ;;
  Linux)
    command -v paplay >/dev/null 2>&1 && paplay /usr/share/sounds/freedesktop/stereo/complete.oga >/dev/null 2>&1 &
    command -v notify-send >/dev/null 2>&1 && notify-send "Derrick" "$MSG" >/dev/null 2>&1
    ;;
esac

echo "🛢️  $MSG"
exit 0
