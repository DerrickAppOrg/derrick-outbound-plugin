---
name: outbound-weekly
description: >-
  Review hebdo des campagnes outbound (boucle d'apprentissage du flow). Lit les réponses de la semaine par
  campagne dans l'outil d'envoi, classe chaque réponse positif/négatif/neutre (avec citation), croise avec le
  ledger (variante A/B, type de signal, chemin de sourcing) pour apprendre CE QUI convertit, met à jour
  leads.jsonl + copy-lessons.md, propose des améliorations de copy, et déclenche le lookalike sur les répondants
  positifs. Déclencheurs : "review outbound", "qui a répondu cette semaine", "analyse les réponses de la
  campagne", "outbound weekly", ou lancé par une routine hebdo planifiée. À lancer depuis la racine du projet
  (spawne des sous-agents).
---

# Outbound weekly — review + apprentissage + lookalike

But : fermer la boucle. L'outil d'envoi dit QUI a répondu ; c'est le croisement **réponse × ledger** qui dit **quel signal / angle / chemin convertit**, et nourrit le copy + le sourcing suivants.

## Pré-requis
- Nos campagnes = celles portant le préfixe défini par le user à l'onboarding (filtrer STRICTEMENT dessus, jamais l'inbox global d'un workspace partagé).
- Ledger : `ledger/leads.jsonl` (chaque lead porte `variant`, `signalType`, `sourcePath`), `copy-lessons.md`, `companies-seen.jsonl`.

## Étape 1 — Récupérer les réponses de la semaine (par campagne)
1. `list_campaigns(search:"<préfixe du user>")` → récupérer les campaignId des nôtres.
2. Pour chacune : `search_conversations(campaignIds:[id], leadReplied:true, lastMessageAtFrom: <il y a 7j en ms>)` → conversations où le lead a répondu.
3. Pour chaque conversation : `get_conversation_messages(conversationId)` → le thread complet (notre message + la réponse).
4. Résoudre le lead : croiser `leadId` avec `leads.jsonl` (via linkedinUrl / nom) pour récupérer variant + signalType + sourcePath.

## Étape 2 — Classer chaque réponse (sous-agent, contexte vierge)
Pour chaque réponse, un juge classe **positif / négatif / neutre** AVEC la citation qui justifie (jamais de label sans preuve) :
- **positif** = intérêt, question, "ok montre-moi", RDV, "c'est quoi".
- **neutre** = "pas maintenant", "recontacte-moi", poli sans intention.
- **négatif** = "non", "stop", agacement, unsubscribe.
Règle d'or : le juge tourne en contexte vierge (sous-agent), pas l'agent qui a écrit le copy.

## Étape 3 — Apprendre (croisement, plain code)
Agréger les réponses classées par : **variant A/B**, **signalType** (news/company/tech/profile/peer-story…), **sourcePath** (chemin de sourcing). Calculer, pour chaque dimension, le **taux de réponse positive**. C'est ça la pertinence :
- quel ANGLE/signal convertit (ex. peer-story > signal entreprise) ;
- quelle VARIANTE (A classique vs B voice + lien ressource) ;
- quel CHEMIN de sourcing ramène les leads qui répondent (boucle "pertinence pas coût" de `outbound-source`).
Écrire les verdicts dans `leads.jsonl` (champ `reply`: positive/negative/neutral + citation) et les enseignements datés dans `copy-lessons.md`.

## Étape 4 — Proposer des améliorations de copy (phase 10)
À partir des gagnants/perdants : proposer 2-3 ajustements concrets de copy pour le prochain batch (ex. "les messages 'coût data' surperforment 'qualité data' → prioriser l'angle coût"). Passer toute nouvelle formulation au gate de `outbound-copy` (check mécanique + humanize + juge en contexte vierge). Ne jamais inventer un enseignement non soutenu par les données.

## Étape 5 — Lookalike sur les positifs (phase 11)
Pour chaque répondant **positif** :
1. Récupérer sa boîte (companyName / linkedinId depuis le dossier d'enrich).
2. `find_similar_companies(linkedinId)` (Derrick) → entreprises similaires.
3. Gate + **dédup contre `companies-seen.jsonl`** (jamais re-scraper) → nouvelles boîtes.
4. Les injecter en tête du pipeline de sourcing (elles ressemblent à ce qui convertit).
Optionnel : régénérer un meilleur prompt/URL de sourcing à partir du profil-type des répondants positifs.

## Garde-fous
- Filtre STRICT sur nos campagnes (préfixe du user), jamais l'inbox partagé.
- Pas de label sans citation ; juge en contexte vierge.
- Répondre/relancer un lead reste une action à confirmer (send_message = envoi réel) — la review PROPOSE, elle n'envoie pas seule.
- Le critère d'apprentissage est la PERTINENCE (taux de réponse positive), pas le coût crédit.

## Sortie
Un rapport hebdo : réponses classées (avec citations), taux de réponse positive par variant/signal/chemin, 2-3 améliorations de copy proposées, liste des lookalikes à sourcer. Loggé dans `ledger/` (reports).
