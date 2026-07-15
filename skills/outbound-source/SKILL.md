---
name: outbound-source
description: >-
  Sourcing outbound DERRICK-FIRST (étape IMPORT du flow). Depuis un ICP précis, choisit le chemin le plus
  PERTINENT parmi 5 (import from prompt / google maps / google+agrégateurs / company from prompt / NAF),
  déduplique contre les registres, qualifie (gate), résout le décideur, et sort une liste de leads propres
  prêts à enrichir. Déclencheurs : "source des leads", "trouve-moi des prospects", "import outbound",
  ou appelée par l'orchestrateur du flow.
---

# Outbound source — IMPORT (Derrick-first)

⛔ **Sourcer avec DERRICK, jamais via l'outil d'envoi.** Critère de choix du chemin = **PERTINENCE des leads**, pas le coût. Appels MCP Derrick **STRICTEMENT séquentiels**.

## Derrick d'abord, web_search Claude en secours (silencieux)
Tout passe par Derrick en priorité. **Les 2 seules étapes nativement gérées par le web_search/WebFetch de Claude** (Derrick n'a pas d'équivalent, ce sont les "🤖" du flow cible) : **(a) parser une page d'agrégateur pour extraire les noms de boîtes**, et **(b) trouver le LinkedIn d'une entreprise sur son propre site**. Partout ailleurs : si un tool Derrick échoue/coince, **fallback silencieux sur le web_search Claude** et on livre la data propre — NE JAMAIS dire à l'user final "Derrick n'a pas trouvé" (il veut le résultat, pas les coulisses).

## Input requis
ICP **précis** (de l'onboarding) : taille (fourchette) + spécialité/vertical + cible prioritaire + fallback de rôle + géo + langue. Refuser un ICP vague.

## Étape 0 — Dédup AVANT toute action (obligatoire)
Charger/consulter les registres `ledger/` : `queries-run.jsonl` (ne pas refaire une recherche), `companies-seen.jsonl` (ne pas re-traiter une boîte, clé=domaine), `leads.jsonl` (ne pas re-contacter, clé=linkedinUrl). MAJ après chaque action.

## Étape 1 — Choisir le CHEMIN (routage par use case, pertinence)
- **Niche pointue / vertical précis** (ex. un type d'agence spécialisée) → **choix 3 (Google + agrégateurs)** : le plus pertinent sur une niche.
- **Cible = secteur d'activité clair** → choix 1 (`import_leads_from_prompt`, 25cr, flou sur niche).
- **Boîtes locales / présence physique** → choix 2 (`google_maps_by_prompt`).
- **Liste de boîtes / ABM** → choix 4 (`import_companies_basic`).
- **Boîtes FR par activité** → choix 5 (`companies_by_naf`).
Consigne : si <30% passent le gate, changer la requête AVANT d'enrichir. Logguer le rendement pour la boucle (pertinence par chemin).

## Étape 2 — Exécuter le chemin choisi
**Choix 1 — import from prompt** : `import_leads_from_prompt(ICP)` → URLs de leads → filtre pertinent (gate).
**Choix 2 — google maps** : `google_maps_by_prompt("<cible> <ville>")` → noms de boîtes → `search_companies` (fallback `serp_first_result` "domaine linkedin company" si "No company found") → décideur.
**Choix 3 — google + agrégateurs** (Derrick-first, meilleur sur niche) :
  1. `serp_first_page("best <vertical> agency <ville>")` → repérer agences directes vs **agrégateurs** (Sortlist/Clutch/GoodFirms…). Booléen `serp` "site:sortlist.fr/s/ <vertical> <ville>" pour cibler un agrégateur.
  2. Si **agrégateur** → lire la page (WebFetch, 0cr — seul trou assumé, Derrick n'extrait pas de liste) → récupérer les noms.
  3. Si **site direct** → trouver le LinkedIn de la boîte sur son site.
  4. `search_companies(nom)` → LinkedIn company (+ `enrich_companies` pour l'id numérique si besoin) → décideur.
**Choix 4 — company from prompt** : `import_companies_basic(url/prompt)` → URLs de company → virer non pertinent → décideur → virer non pertinent.
**Choix 5 — NAF** : `companies_by_naf(code, dept)` → noms → `search_companies` (fallback serp) → décideur.

## Étape 3 — Résoudre le DÉCIDEUR (Derrick)
- **CIBLE** = `search_leads_in_companies` (company id + critères Sales Nav founder/CEO/Head of Sales). ⚠️ **BUGGÉ** (filtre company ignoré, bug backend) → ne pas utiliser tant que pas fixé.
- **WORKAROUND actuel** = `find_staff_members` (URL company, `currentFunction` pour cibler direction ; 1cr/personne → 1 appel/boîte, repérer le fondateur, ne pas itérer).
- Fallback silencieux : WebSearch (ne jamais dire "Derrick n'a pas trouvé" à l'user final).

## Étape 4 — GATE de qualification (AVANT enrich)
Lire headline + site : est-ce VRAIMENT la cible ICP ? EXCLURE : hors-ICP, concurrents, clients existants, la blacklist définie par le user, et ce qui pollue l'annuaire (ex. une requête large ramène des métiers adjacents → virer). Fit STRICT : borderline → sort. Un lead ne passe au enrich QUE s'il passe le gate.

## Output
Liste de leads qualifiés (nom + boîte + LinkedIn profil + company id) avec leur `sourcePath` (chemin utilisé), prêts pour `outbound-enrich`. Registres à jour (queries-run, companies-seen). Rendement loggé (résultats bruts / gardés après gate) pour la boucle de pertinence.
