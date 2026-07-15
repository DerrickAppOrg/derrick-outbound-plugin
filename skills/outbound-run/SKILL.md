---
name: outbound-run
description: >-
  Orchestrateur du flow outbound autonome (Import → Enrichissement → Message → Séquence → Push → boucle
  d'apprentissage). Enchaîne les skills du moteur outbound, précédé du mini-onboarding qui capte le spécifique
  du user. Déclencheurs : "lance le flow outbound", "fais tourner la prospection", "run outbound", ou premier
  lancement après install du plugin. À lancer depuis la racine du projet (spawne des sous-agents ; un
  sous-agent ne peut pas en spawner un autre).
---

# Outbound run — orchestrateur du flow

Enchaîne le moteur. Chaque étape = une skill dédiée (`outbound-source`, `outbound-enrich`, `outbound-copy`, `outbound-sequence`, `outbound-push`, `outbound-weekly`). Principe transverse : **DERRICK-FIRST**, fallback web_search Claude silencieux ; critère = **PERTINENCE pas coût** ; **dédup obligatoire** (registres) ; appels Derrick **séquentiels** ; **annoncer le coût crédits** avant toute action Derrick facturée et attendre le go.

## Phase 0 — ONBOARDING (1re fois / plugin)
Capter le SPÉCIFIQUE du user (le moteur est générique). Les 8 étapes du mini-onboarding :
1. **Connexions** : Derrick (moteur data, requis) + outil d'envoi (Lemlist et autres à venir ; sinon fallback export CSV/API). Clés en secrets locaux, jamais dans le plugin.
2. **Offre + ICP PRÉCIS** : déduire du site + questions → forcer taille + spécialité + cible prioritaire + fallback de rôle (refuser le vague).
3. **Produit/service vendu** : ce que le user vend (le moteur s'y adapte, il ne vend pas un produit en dur).
4. **Style/voix** : `outbound-copy` analyse les conversations Claude passées du user (en le disant) → exemples → validation.
5. **Crédibilité/USP** du user (parcours, preuves → pair-à-pair).
6. **Exclusions** : concurrents, clients existants, blacklist définie par le user.
7. **Langue(s)** de la prospection.
8. **Récap + validation** de la config avant le premier run.

## Phase 1 — SOURCING → skill `outbound-source`
Routage par use case (5 chemins), dédup, gate. Sort des leads qualifiés + leur `sourcePath`. **Valider avec l'user avant de dépenser** (requête + estimation crédits).

## Phase 2 — ENRICHISSEMENT → skill `outbound-enrich`
Profil + entreprise + news + tech (stop-on-signal), signal croisé. Sous-agent séquentiel pour les lots.

## Phase 3 — MESSAGE → skill `outbound-copy`
DM1 perso (2 phrases, voix du user, reformulation≠paraphrase, ne pas attaquer une force) + relances. Gate lint+humanize+juge en contexte vierge. **Montrer un batch de test à l'user pour validation ("c'est moi / pas moi")** avant d'industrialiser.

## Phase 4 — SÉQUENCE → skill `outbound-sequence`
RECO dans le chat (canal, nb messages, espacement, branches). Livrer le contenu bloc par bloc. Le user monte la séquence dans son outil lui-même.

## Phase 5 — PUSH → skill `outbound-push`
Mapping attributs + split A/B + **check pré-push 2 passes anti-collision** + vérif URLs. Leads dans l'audience du user.

## Phase 6 — LAUNCH (manuel user)
Pas de tool MCP pour lancer/créer une campagne → le launch reste un clic de l'user. L'orchestrateur s'arrête ici et confirme ce qui reste à faire côté user (renommer/vérifier blocs, attacher audience, enregistrer voice, lancer).

## Phase 7 — BOUCLE → skill `outbound-weekly` (routine hebdo séparée)
Une fois lancé : review hebdo (réponses pos/neg/neutre × ledger → pertinence par signal/chemin → copy-lessons + amélioration + lookalike). À planifier en routine (cron) démarrant après le launch.

## Garde-fous
Le flow PROPOSE et fait valider aux étapes sensibles (sourcing, copy, launch) ; il n'envoie jamais seul. Jamais de fausse perso.
