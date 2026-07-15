---
name: outbound-enrich
description: >-
  Enrichissement outbound (étape ENRICHISSEMENT du flow), Derrick-first. Pour chaque lead qualifié, enrichit
  entreprise + profil + signaux en cascade stop-on-signal, et sort un dossier avec LE signal exploitable
  (idéalement croisé) pour l'icebreaker. Déclencheurs : "enrichis ces leads", "trouve les signaux", ou appelée
  par l'orchestrateur après outbound-source.
---

# Outbound enrich — ENRICHISSEMENT (Derrick-first)

Appels MCP Derrick **STRICTEMENT séquentiels** (jamais 2 dans le même bloc). Pour des lots >~5 leads, déléguer à un sous-agent (séquentiel), budget annoncé.

## Pipeline par lead (~3-4 cr, stop-on-signal)
1. `enrich_profile(url)` → headline, bio, ancienneté, parcours, ce qu'il publie.
2. `enrich_companies(company url)` → taille, secteur, description, site, spécialités.
3. `google_news(companyName, period:"90d", language)` → actualité datée (levée, rachat, recrutement…). NB : souvent vide sur les TPE.
4. **Stop-on-signal** : si 1-3 n'ont pas donné de signal fort → `find_tech(site)` (2cr) puis `serp` sur le fondateur/la boîte. On NE déclenche 4 que si nécessaire (coût maîtrisé).

## Choisir LE signal (hiérarchie + CROISEMENT)
Hiérarchie adaptée à l'ICP : news > signal entreprise (croissance, recrutement SDR, techno) > tech stack > contenu/profil fondateur > douleur du rôle. ⚠️ Sur beaucoup de cibles la news est vide → le signal réel est le profil/contenu.
**CROISER** pour la pertinence : news × prise de poste récente ≠ news × grande ancienneté ; techno × offre ; contenu × douleur. Le croisement enrichit l'ANGLE, jamais la longueur (accroche toujours très courte).
Jamais de fausse perso : aucun signal fort → angle générique du segment, on n'invente pas.

## Output
Un dossier par lead : identité + boîte (taille/secteur) + **LE signal retenu (factuel, sourcé, jamais inventé)** + type de signal (pour le ledger). Prêt pour `outbound-copy`.
