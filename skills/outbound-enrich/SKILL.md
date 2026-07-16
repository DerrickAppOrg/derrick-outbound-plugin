---
name: outbound-enrich
description: >-
  Enrichissement outbound (étape ENRICHISSEMENT du flow), Derrick-first. Pour chaque lead qualifié, enrichit
  entreprise + profil + signaux en cascade stop-on-signal, et sort un dossier avec LE signal exploitable
  (idéalement croisé) pour l'icebreaker. Déclencheurs : "enrichis ces leads", "trouve les signaux", ou appelée
  par l'orchestrateur après outbound-source.
---

# Outbound enrich — ENRICHISSEMENT (Derrick-first)

## Parallélisation
- **Séquentiels : les appels LinkedIn UNIQUEMENT** (`enrich_profile`, `enrich_companies`, imports LinkedIn) — jamais 2 dans le même bloc, sinon réponses mélangées + timeouts.
- **Tout ce qui n'est PAS LinkedIn se parallélise** : `google_news`, `find_tech` (site), `serp`, WebFetch. Ex. : `enrich_profile` **pendant** `google_news` ; tech stack (site) **pendant** un appel LinkedIn.
- Si l'enrichissement fait attendre le user **> 1 min** → prévenir (café) **en expliquant que c'est du live = data fraîche**, et enchaîner en parallèle ce qui peut l'être (typiquement démarrer la copy).

## ⛔ DIGEST immédiat — jamais le JSON brut (le vrai poste de coût)
Le coût du flow n'est pas la longueur des skills, c'est le **volume de data brute qui entre dans le contexte** : chaque `enrich_profile` / `enrich_companies` / `google_news` renvoie un gros JSON (bio, parcours, formations, skills…), × 3 appels × N leads.
- ⛔ **Ne JAMAIS garder ni recracher un JSON de réponse brut.** Dès qu'un appel revient : extraire les champs utiles, écrire la ligne, **jeter le reste**.
- **Champs retenus, rien d'autre** : prénom/nom, URL profil, headline/rôle, boîte, taille, secteur, 1 signal daté + sa source, langue. **Pas** la bio intégrale, **pas** le parcours complet, **pas** les formations, **pas** la liste de skills.
- ⛔ **Jamais afficher les dossiers de leads dans le chat** (ni tableau, ni liste). Ils vivent sur disque ; échantillon seulement si le user le demande.

## ⛔ Batching + écriture disque (sinon le sous-agent meurt de contexte)
- Lots >~5 leads : déléguer à un sous-agent (LinkedIn séquentiel à l'intérieur), **après accord du user** (plus rapide, mais plus de tokens) et budget crédits annoncé.
- ⛔ **JAMAIS un seul sous-agent pour tout le lot.** Batcher par **5 à 8 leads MAXIMUM** par sous-agent : au-delà, l'accumulation des JSON le tue. Constaté en test réel : un sous-agent chargé de 41 leads s'est figé **silencieusement au 17e**.
- ⛔ **Écrire sur DISQUE au fil de l'eau, pas dans le contexte** : dès qu'un lead est enrichi, sa ligne digest est **appendée immédiatement** au fichier de sortie (**1 ligne JSONL par lead**). Le sous-agent ne conserve rien en mémoire.
- ⛔ **Le sous-agent ne retourne QUE** : nb traités + chemin du fichier + les leads en échec. **JAMAIS les données**, jamais un dump de fiches.
- **Reprise sur incident (obligatoire)** : le fichier sur disque est la **source de vérité**. Si un sous-agent meurt, on relit le fichier et on repart du dernier lead écrit → **zéro travail perdu, zéro crédit re-brûlé**. C'est le batching + l'écriture disque qui rendent l'enrichissement reprenable ; sans eux, un lot long est une bombe à retardement.
- **Vérifier la PROGRESSION, pas la vivacité** : un sous-agent bloqué et un sous-agent lent se ressemblent. Le seul juge = **l'horodatage de la dernière ligne écrite sur disque**. S'il ne bouge plus depuis plusieurs minutes → il est mort : reprendre depuis le fichier. Ne jamais attendre indéfiniment, ni annoncer « ça avance » au user sans preuve fraîche.

## Pipeline par lead (~3-4 cr, stop-on-signal)
1. `enrich_profile(url)` → headline, bio, ancienneté, parcours, ce qu'il publie.
2. `enrich_companies(company url)` → taille, secteur, description, site, spécialités.
3. `google_news(companyName, period:"90d", language)` → actualité datée (levée, rachat, recrutement…). Parallélisable avec 1-2. NB : souvent vide sur les TPE — **`no news found` n'est PAS une erreur**, ne jamais l'afficher comme "Error" : « pas de news récente sur cette boîte », on continue la cascade.
4. **Stop-on-signal** : si 1-3 n'ont pas donné de signal fort → `find_tech(site)` (2cr) puis `serp` sur le fondateur/la boîte. On NE déclenche 4 que si nécessaire (coût maîtrisé).

## Choisir LE signal (hiérarchie + CROISEMENT)
Hiérarchie adaptée à l'ICP : news > signal entreprise (croissance, recrutement SDR, techno) > tech stack > contenu/profil fondateur > douleur du rôle. ⚠️ Sur beaucoup de cibles la news est vide → le signal réel est le profil/contenu.
**CROISER** pour la pertinence : news × prise de poste récente ≠ news × grande ancienneté ; techno × offre ; contenu × douleur. Le croisement enrichit l'ANGLE, jamais la longueur (accroche toujours très courte).
Jamais de fausse perso : aucun signal fort → angle générique du segment, on n'invente pas.

## ⛔ Fin de phase — SONNER le user (il est parti prendre un café)
Le user a été prévenu que c'était long, il a lâché son écran. **Dès que le dernier lead est enrichi, AVANT de résumer** : lancer
```
bash "${CLAUDE_PLUGIN_ROOT}/scripts/notify-done.sh" <nb_leads> enrich
```
→ cloche + notif desktop + une phrase Derrick (le derrick = la tour de forage : « le puits a donné »). Ne PAS l'appeler par lead (une fois par phase), ni sur une phase courte (< 1 min). Le user peut couper avec `DERRICK_NOTIFY=0`.

## Output
Un dossier par lead : identité + boîte (taille/secteur) + **LE signal retenu (factuel, sourcé, jamais inventé)** + type de signal (pour le ledger). Prêt pour `outbound-copy`.
