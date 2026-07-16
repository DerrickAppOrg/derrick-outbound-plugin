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
Tout passe par Derrick en priorité. **Les 2 seules étapes nativement gérées par le web_search/WebFetch de Claude** (Derrick n'a pas d'équivalent) : **(a) parser une page d'agrégateur pour extraire les noms de boîtes**, et **(b) trouver le LinkedIn d'une entreprise sur son propre site**. Partout ailleurs : si un tool Derrick échoue/coince, **fallback silencieux sur le web_search Claude** et on livre la data propre — NE JAMAIS dire à l'user final "Derrick n'a pas trouvé" (il veut le résultat, pas les coulisses).

## Input requis
ICP **précis** (de l'onboarding) : taille (fourchette) + spécialité/vertical + cible prioritaire + fallback de rôle + géo + langue. Refuser un ICP vague.

## Volume (limites)
- **Premier sourcing** : viser **~50 leads qualifiés** (limite basse au 1er run, pour amorcer sans exploser le budget).
- **En boucle hebdo** (relancé par `outbound-weekly`) : **20 à 40 nouveaux** leads par cycle (dédup stricte vs `companies-seen`/`leads.jsonl`).

## Étape 0 — Dédup AVANT toute action (obligatoire)
Charger/consulter les registres `ledger/` : `queries-run.jsonl` (ne pas refaire une recherche), `companies-seen.jsonl` (ne pas re-traiter une boîte, clé=domaine), `leads.jsonl` (ne pas re-contacter, clé=linkedinUrl). MAJ après chaque action.

## ⛔ Étape 0bis — TYPE DE CIBLE avant tout routage
Avant de choisir un chemin, déterminer si la cible a une **présence LinkedIn exploitable** :
- **B2B / structures avec LinkedIn** (agences, SaaS, cabinets, PME tech…) → chemins LinkedIn OK (`search_companies`, décideur, etc.).
- **Commerce local / TPE physique** (café, resto, boutique, artisan…) → **partir de `google_maps_by_prompt`** (fiche = nom, tel, **site**, avis). Depuis le site, DEUX options selon ce qu'on cherche : **(a) `website_contact_social`** (email/tel/socials du site) ou **(b) tenter le search LinkedIn** (`search_companies` / serp). LinkedIn n'est PAS interdit sur ces cibles, ce n'est simplement pas le point de départ : Maps d'abord, puis on choisit la voie selon ce qu'on a trouvé.
- ⛔ **EXPLOITER ce que Maps a déjà donné** : la fiche `google_maps_by_prompt` retourne DÉJÀ nom + téléphone + **site** + adresse + avis. Ne JAMAIS relancer un `serp_first_result` / `search_companies` pour retrouver une info que Maps vient de fournir. Après Maps → on part directement du **site** (→ `website_contact_social` pour les contacts, ou tenter LinkedIn si on a besoin du décideur). Re-chercher ce qu'on a déjà en main = crédits brûlés (raté observé : Maps avait sorti une vingtaine de boîtes AVEC leurs sites, et le flow a quand même enchaîné un serp LinkedIn par boîte).
- En cas de doute → un test rapide (1 boîte) avant de lancer le lot.
**Cas réel du raté** : cible = un commerce local (un café dans une ville donnée) → le flow a tenté LinkedIn en direct et **accepté un hôtel sans rapport comme match**. Le problème n'est PAS d'avoir tenté LinkedIn, c'est d'avoir accepté un match faux sans vérification (voir règle ci-dessous).

## ⛔ Vérification de COHÉRENCE du match (obligatoire, tout chemin)
Tout résultat de `search_companies` / `serp` doit être **vérifié contre le nom et le contexte de la cible** avant d'enchaîner. Si le nom retourné ne correspond pas (ex. on cherche un café précis, le résultat est un hôtel d'une autre enseigne), **REJETER** : ne jamais enchaîner un enrichissement sur un match non vérifié. Un mauvais match pollue tout le lot en aval.

## Étape 1 — Choisir le CHEMIN (routage par use case, pertinence)
- **Niche pointue / vertical précis** (ex. un type d'agence spécialisée) → **choix 3 (Google + agrégateurs)** : le plus pertinent sur une niche.
- **Cible = secteur d'activité clair** → choix 1 (`import_leads_from_prompt`, 25cr, flou sur niche).
- **Boîtes locales / présence physique** → choix 2 (`google_maps_by_prompt`).
- **Liste de boîtes / ABM** → choix 4 (`import_companies_basic`).
- **Boîtes FR par activité** → choix 5 (`companies_by_naf`).
Consigne : si <30% passent le gate, changer la requête AVANT d'enrichir. Logguer le rendement pour la boucle (pertinence par chemin).

## Étape 2 — Exécuter le chemin choisi
**Choix 1 — import from prompt** : `import_leads_from_prompt(ICP)` → URLs de leads → filtre pertinent (gate).
**Choix 2 — google maps** : `google_maps_by_prompt("<cible> <ville>")` → nom + tel + **site** + adresse + avis, DÉJÀ dans la fiche (ne pas les re-chercher) → depuis le site, SOIT `website_contact_social` (contacts du site) SOIT, si on a besoin du décideur, `search_companies` (fallback `serp_first_result` "domaine linkedin company" si "No company found") → décideur. **Vérifier la cohérence du match avant d'enchaîner.**
**Choix 3 — google + agrégateurs** (Derrick-first, meilleur sur niche) :
  1. `serp_first_page("best <vertical> agency <ville>")` → repérer agences directes vs **agrégateurs** (annuaires de prestataires). Booléen `serp` "site:<annuaire> <vertical> <ville>" pour cibler un agrégateur.
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
Lire headline + site : est-ce VRAIMENT la cible ICP ? EXCLURE : hors-ICP, concurrents, clients existants, les exclusions / la blacklist définies par l'user à l'onboarding, et ce qui pollue l'annuaire (ex. une requête large ramène des métiers adjacents → virer). Fit STRICT : borderline → sort. Un lead ne passe au enrich QUE s'il passe le gate.

## Output
Liste de leads qualifiés (nom + boîte + LinkedIn profil + company id) avec leur `sourcePath` (chemin utilisé), prêts pour `outbound-enrich`. Registres à jour (queries-run, companies-seen). Rendement loggé (résultats bruts / gardés après gate) pour la boucle de pertinence.
