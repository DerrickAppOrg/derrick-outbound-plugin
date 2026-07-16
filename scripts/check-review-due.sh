#!/usr/bin/env bash
# Rappel de la review hebdo outbound, au démarrage d'une session.
#
# Pourquoi ce hook existe : la boucle d'apprentissage est ce qui fait la
# valeur du flow, et rien ne peut la déclencher automatiquement. Les crons
# de session (CronCreate) meurent à la fermeture du terminal, et tout le
# monde n'a pas de planificateur durable. Le seul moment fiable où l'on
# sait que l'utilisateur est là, c'est quand il ouvre une session.
#
# Règle du jeu : SILENCIEUX tant qu'il n'y a rien à dire. Un rappel qui
# s'affiche à chaque démarrage devient un rappel qu'on n'ouvre plus.
#
# Sortie : rien (exit 0), ou un JSON {"additionalContext": "..."} que
# Claude lit comme du contexte. cwd = le projet de l'utilisateur.
set -uo pipefail

LEDGER="./ledger"
STAMP="$LEDGER/.last-review"
LEADS="$LEDGER/leads.jsonl"
SEUIL_JOURS=7

# Pas de flow outbound dans ce projet : ne rien dire.
[ -d "$LEDGER" ] || exit 0
[ -s "$LEADS" ] || exit 0

# Rien n'est parti en campagne : il n'y a aucune réponse à analyser.
grep -q '"status"[[:space:]]*:[[:space:]]*"pushed"' "$LEADS" 2>/dev/null || exit 0

now=$(date +%s)

if [ -f "$STAMP" ]; then
  # Le stamp contient un timestamp epoch en premier champ (portable :
  # `date -d` est GNU, `date -j` est BSD, aucun des deux n'est partout).
  last=$(cut -d' ' -f1 < "$STAMP" 2>/dev/null | tr -dc '0-9')
  [ -n "$last" ] || last=0
  jours=$(( (now - last) / 86400 ))
  [ "$jours" -lt "$SEUIL_JOURS" ] && exit 0
  msg="La review outbound n'a pas tourne depuis ${jours} jours. Les reponses recues ne sont donc pas analysees, et la boucle d'apprentissage (quel signal et quel chemin ramenent des reponses) n'apprend rien tant qu'elle ne tourne pas. Proposer a l'utilisateur de lancer la skill outbound-weekly : elle analyse et propose, elle n'envoie rien."
else
  msg="Des leads sont en campagne mais la review outbound n'a jamais tourne. C'est elle qui lit les reponses et fait apprendre la boucle (copy, signaux, lookalikes). Proposer a l'utilisateur de lancer la skill outbound-weekly : elle analyse et propose, elle n'envoie rien."
fi

# JSON assemble a la main : ni jq ni python ne sont garantis chez l'user.
# Le message est volontairement sans guillemets ni antislash.
printf '{"additionalContext": "%s"}\n' "$msg"
exit 0
