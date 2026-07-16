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
- Nos campagnes = celles portant le préfixe défini par l'user à l'onboarding (filtrer STRICTEMENT dessus, jamais l'inbox global).
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

## Étape 4 — Proposer des améliorations de copy
À partir des gagnants/perdants : proposer 2-3 ajustements concrets de copy pour le prochain batch (ex. "les messages 'coût data' surperforment 'qualité data' → prioriser l'angle coût"). Passer toute nouvelle formulation au gate de `outbound-copy` (check mécanique + humanize + juge en contexte vierge). Ne jamais inventer un enseignement non soutenu par les données.

## Étape 5 — Lookalike sur les positifs — RÉUTILISE la logique d'import de `outbound-source`
Pour chaque répondant **positif** :
1. Récupérer sa boîte (companyName / linkedinId depuis le dossier d'enrich).
2. `find_similar_companies(linkedinId)` (Derrick) → entreprises similaires.
3. **Trouver les leads (décideurs) derrière** ces boîtes : c'est la MÊME logique que `outbound-source` (divers chemins selon ce qu'on obtient : nom→`search_companies`, fallback serp/web, résolution décideur via `find_staff_members`/`search_leads_in_companies`, vérification de cohérence du match, gate). Le lookalike n'est pas un tunnel figé : selon ce que `find_similar_companies` rend (id, nom, site), on route vers le bon chemin, exactement comme à l'import.
4. **La différence = le CONTEXTE d'apprentissage impulse le choix de la méthode** : on privilégie le chemin/le signal/l'angle qui a le mieux CONVERTI (pas juste passé le gate). Ex. si "signal X via chemin Y" a le meilleur taux de réponse positive, le lookalike vise ce type de boîtes par ce chemin en priorité.
5. Gate + **dédup contre `companies-seen.jsonl`/`leads.jsonl`** (jamais re-scraper/re-contacter).
**Volume boucle : 20 à 40 nouveaux leads par cycle** (le 1er sourcing hors boucle vise ~25). Injecter en tête du pipeline (`outbound-source`→`enrich`→`copy`→`push`).
Optionnel : régénérer un meilleur prompt/URL de sourcing à partir du profil-type des répondants positifs.

## Voies de la boucle (figées)
Selon CE QUE l'apprentissage révèle, on choisit — faisabilité Derrick vérifiée :
| # | Voie | Faisable | Quand l'apprentissage montre que… |
|---|---|---|---|
| 1 | **Lookalike entreprise** → résoudre décideurs | ✅ `find_similar_companies` | les BOÎTES d'un profil convertissent |
| 2 | **Refaire le chemin gagnant** (autres villes/verticaux/annuaires) | ✅ tous les imports Derrick | un CHEMIN de sourcing convertit (filon à étendre) |
| 3 | **Sourcing par SIGNAL** | ✅ news via `google_news` ; le reste (voir liste) via **web_search Claude** | un TYPE DE SIGNAL convertit, peu importe la boîte |
| 4 | **ICP raffiné** → relancer `outbound-source` | ✅ imports Derrick | un pattern d'ICP net se dégage sur la même cible |
| 5 | **Élargir dans les mêmes boîtes** (autres décideurs) | ✅ `find_staff_members` | les boîtes cibles ont plusieurs décideurs |
| 6 | **NOUVEL ICP (autre segment) = 2e FLOW COMPLET** | ✅ tout `outbound-source`, mais nouveau flow | on a un **process SCALABLE prouvé sur l'ICP 1** → on GARDE le flow ICP 1 qui tourne ET on crée un **2e flow complet** : 2e campagne + 2e ton/voix + 2e séquence + 2e messaging. ⛔ **VALIDATION USER OBLIGATOIRE** (mini-onboarding du nouveau segment : ICP + ton/voix). |

**Signaux à chercher via web_search Claude (voie 3)** : changement de poste récent (job change), levée de fonds, recrutement (SDR / sales / hiring), rachat / acquisition, forte croissance / nouveau bureau, lancement de produit. `google_news` reste la voie native pour l'actu/rachat.

Une voie "engagers d'un post LinkedIn" a été écartée : elle nécessite d'ajouter l'URL du post à la main → pas automatisable dans la boucle.

Toutes les voies (sauf la 6) convergent sur : gate → dédup → enrich → copy → push, **20-40 nouveaux/cycle**. La voie 6 est un flow parallèle distinct.

## Garde-fous
- Filtre STRICT sur nos campagnes (préfixe du user), jamais l'inbox partagé.
- Pas de label sans citation ; juge en contexte vierge.
- Répondre/relancer un lead reste une action à confirmer (send_message = envoi réel) — la review PROPOSE, elle n'envoie pas seule.
- Le critère d'apprentissage est la PERTINENCE (taux de réponse positive), pas le coût crédit.

## ⛔ Dernière étape, obligatoire : horodater le run
```
date +"%s %Y-%m-%d" > ledger/.last-review
```
**Toujours**, même si le run n'a rien trouvé (0 réponse = un run quand même). C'est ce fichier que lit le hook `SessionStart` du plugin pour rappeler la review quand elle n'a pas tourné depuis 7 jours. Sans cette ligne, **le rappel ne s'éteint jamais** et devient du bruit qu'on apprend à ignorer.

## Sortie
Un rapport hebdo : réponses classées (avec citations), taux de réponse positive par variant/signal/chemin, 2-3 améliorations de copy proposées, liste des lookalikes à sourcer. Loggé dans `ledger/` (reports).
