---
name: outbound-copy
description: >-
  Écrit les messages outbound (étape MESSAGE du flow) à la VOIX du user. Capte son ton en analysant ses
  conversations Claude passées, cale le fit ICP, rédige le DM1 perso (2 phrases) + les relances, et passe
  tout au gate (lint + humanize + juge en contexte vierge). Déclencheurs : "écris les messages", "rédige les
  DM", ou appelée après outbound-enrich.
---

# Outbound copy — MESSAGE (à la voix du user)

## Étape 1 — Capter la VOIX du user (une fois, à l'onboarding)
Analyser les **conversations Claude passées du user** (le lui DIRE) via les tools de session (`list_sessions`, `search_session_transcripts`) → repérer ses tics : minuscules, abréviations, connecteurs oraux, ponctuation, niveau d'imperfection. Montrer 2-3 exemples de ce que ça donnera → l'user valide/ajuste. Ne JAMAIS copier les tics d'un autre user : capter CE user, pas un style générique.

## Étape 2 — Fit ICP + registre
Ton adapté à la cible : tu (pairs/founders TPE) vs vous (PME 150+, séniors/corporate, boîtes historiques/rachetées). Doute → vous.

## Étape 3 — Écrire (règles DURES)
- **DM1 = 2 phrases MAX**, ouvre sur le signal réel (de outbound-enrich), pose une vraie question (ou pas — le 1er message peut ne pas finir par une question).
- **Reformulation JAMAIS paraphrase** : ne jamais reprendre les faits/chiffres du profil de façon reconnaissable. Un humain ne recrache pas la fiche → parler de la réalité vécue du prospect sans réciter aucun data point.
- **Ne JAMAIS attaquer une force** du prospect (ex. multi-enrichissement = souvent mieux que simple). Pas d'angle sur une fausse faiblesse.
- **Imperfections humaines** dosées (~1 msg/2-3), VARIÉES, jamais dupliquées entre 2 messages (signature de template = grillé, le milieu est petit).
- **Varier les questions de clôture** ; une seule question "famille data/fichiers" par lot.
- **Pair-à-pair** : le background du user (son parcours, ses USP) crée la crédibilité.
- Relances : courtes, dans la voix, n'apportent que du neuf (jamais une redite du DM1 ; structure de séquence : `outbound-sequence`).

## Étape 4 — GATE (obligatoire avant push)
Avant de pousser tout message : (1) check mécanique (pas de tics IA / em-dash / formule interdite), (2) passe de relecture "humanize" (retirer le ton robotique, restaurer la cadence humaine), (3) un juge qui note la qualité en **contexte vierge** — un sous-agent dédié, jamais l'agent qui a écrit le message (un writer ne s'auto-note pas). Retry sur les défauts.

## Mapping attributs (sortie → outbound-push)
CA1 = message DM1 · CA3 = type de signal · CA4 = lien ressource (présent = branche B) · CA6 = langue. (CA2 icebreaker oral = INUTILE : le voice de l'outil d'envoi ne personnalise que le prénom.)
