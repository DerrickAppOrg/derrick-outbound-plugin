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

Enchaîne le moteur. Chaque étape = une skill dédiée (`outbound-source`, `outbound-enrich`, `outbound-copy`, `outbound-sequence`, `outbound-push`, `outbound-weekly`). Principe transverse : **DERRICK-FIRST**, fallback web_search Claude silencieux ; critère = **PERTINENCE pas coût** ; **dédup obligatoire** (registres) ; appels **LinkedIn** Derrick séquentiels (le reste se parallélise, voir ci-dessous) ; **annoncer le coût crédits RÉEL** avant toute action Derrick facturée (au résultat facturé, pas "par appel" — ex. `import_leads_from_prompt` = ~25cr/page) et attendre le go.

## Parallélisation & attente
- **Séquentiel obligatoire : les appels LinkedIn uniquement** (`enrich_profile`, `enrich_companies`, `search_companies`, imports LinkedIn…) — en parallèle, les réponses se mélangent + timeouts.
- **Tout le reste se parallélise** : `google_news`, `find_tech`/site, `serp`, WebFetch, lecture de registres. Ex. valide : profil LinkedIn (séquentiel) **pendant** google_news, ou tech stack (site) **pendant** un appel LinkedIn.
- **Règle d'attente** : dès qu'une action fait attendre le user **> 1 minute** et qu'une autre action peut tourner en parallèle → **le faire**, sauf si ça dégrade le flow ou la qualité. Exemple : démarrer la **phase COPY pendant que l'enrichissement tourne en fond**.

## Économie de tokens (transverse)
**Le flow ne doit pas griller les tokens du user.** Ordre des leviers : (1) ne pas faire entrer la data brute dans le contexte (**digest**, voir `outbound-enrich`), (2) ne pas la ressortir dans le chat, (3) être bref.
- ⛔ **Pas de récap après chaque étape**, pas de tableau décoratif, pas de re-dump des dossiers, pas de reformulation de ce que le user vient de dire. Étape finie = **1 à 2 lignes** (ce qui est fait + ce qui suit).
- **Lire ciblé, pas en entier** : grep/tranche précise plutôt qu'un fichier complet ; les registres se consultent **par clé**, jamais en les dumpant.
- **Ne jamais relire un fichier qu'on vient d'écrire** pour vérifier.
- **Sous-agent = résumé dense**, jamais les données : le fichier sur disque est la source de vérité.

## UX — quand solliciter le user (et quand se taire)
- **Ne JAMAIS demander la permission pour écrire/sauvegarder les registres (`ledger/`)** : on le fait, point. On ne sollicite le user QUE sur le **workflow** : cible, copy, dépenses de crédits, envois.
- **Sous-agent = accord préalable** : avant de déléguer un lot à un sous-agent, expliquer le compromis (**plus rapide, mais consomme plus de tokens**) et demander si c'est ok.
- **Enrichissement long = message positif** : prévenir que ça prend du temps (« allez prendre un café ») **en expliquant pourquoi** : l'enrichissement se fait **EN LIVE**, ce qui garantit la fraîcheur et la qualité de la data (ce n'est pas une base figée). C'est un argument, pas une excuse.
- **`no news found` n'est PAS une erreur** : ne jamais l'afficher comme "Error". Le dire calmement (« pas de news récente sur cette boîte ») et continuer la cascade.

## Phase 0 — ONBOARDING (1re fois / plugin)
Capter le SPÉCIFIQUE du user (le moteur est générique). Les étapes du mini-onboarding :
1. **Connexions** : Derrick (moteur data, requis) + outil d'envoi (La Growth Machine aujourd'hui ; Lemlist et autres à venir ; sinon fallback export CSV/API). Clés en secrets locaux, jamais dans le plugin.
   - ⛔ **Vérifier la session LinkedIn (li_at) AU DÉBUT, par un appel test** (1 `enrich_profile` sur un profil connu). Les features LinkedIn de Derrick exigent que le user ait **connecté sa session LinkedIn via l'extension Chrome Derrick** ; sans ça les tools LinkedIn renvoient **vide/erreur**. Si non connecté → **guider l'installation/connexion de l'extension avant d'aller plus loin**. Ne JAMAIS lancer un sourcing LinkedIn sans ce check.
2. **Offre + ICP PRÉCIS** : déduire du site + questions → forcer taille + spécialité + cible prioritaire + fallback de rôle (refuser le vague).
3. **Produit/service vendu** : ce que le user vend (le moteur s'y adapte, il ne vend pas un produit en dur).
4. **PRICING du produit du user (obligatoire)** : demander/vérifier le **prix réel de ce qu'il vend** — y a-t-il un plan gratuit/freemium ? à partir de quel prix ? la fonctionnalité mise en avant est-elle accessible en gratuit ? Sert à ne **jamais écrire de bêtise prix dans le copy** (raté classique : « c'est gratuit pour commencer » alors que la feature vendue exige un plan payant). Doute → pas de mention de prix.
5. **Style/voix** : `outbound-copy` analyse les conversations Claude passées du user (en le disant) → exemples → validation.
6. **Crédibilité/USP** du user (parcours, preuves → pair-à-pair).
7. **Exclusions** : concurrents, clients existants, blacklist définie par le user.
   - ⛔ **Faire lister les concurrents EXPLICITEMENT** (= qui vend le même produit que lui). Ne jamais déduire d'exclusions de son **parcours passé** : un ex-fondateur d'agence n'a pas les agences pour concurrents — c'est souvent sa cible.
8. **Langue(s)** de la prospection.
9. **Récap + validation** de la config avant le premier run.

## Phase 1 — SOURCING → skill `outbound-source`
Routage par use case (5 chemins), dédup, gate. Sort des leads qualifiés + leur `sourcePath`. **Valider avec l'user avant de dépenser** (requête + estimation crédits).

## Phase 2 — ENRICHISSEMENT → skill `outbound-enrich`
Profil + entreprise + news + tech (stop-on-signal), signal croisé. **Digest immédiat, jamais le JSON brut** ; écriture disque au fil de l'eau ; batch de 5-8 leads/sous-agent. Applique les règles de parallélisation, d'attente et d'UX ci-dessus.

## Phase 3 — MESSAGE → skill `outbound-copy`
DM1 perso (2 phrases, voix du user, reformulation≠paraphrase, ne pas attaquer une force) + relances. Gate lint+humanize+juge en contexte vierge. **Montrer un batch de test à l'user pour validation ("c'est moi / pas moi")** avant d'industrialiser.

## Phase 4 — SÉQUENCE → skill `outbound-sequence`
RECO dans le chat (canal, nb messages, espacement, branches). Livrer le contenu bloc par bloc. Le user monte la séquence dans son outil lui-même.

## Phase 5 — PUSH → skill `outbound-push`
Mapping attributs + split A/B + vérif des URLs post-push. Leads dans l'audience du user.

## Phase 6 — LAUNCH (manuel user)
Pas de tool MCP pour lancer/créer une campagne → le launch reste un clic de l'user. L'orchestrateur s'arrête ici et confirme ce qui reste à faire côté user (renommer/vérifier blocs, attacher audience, enregistrer voice, lancer).

## Phase 7 — BOUCLE → skill `outbound-weekly` ⛔ À PLANIFIER, PAS À MENTIONNER
Review hebdo : réponses pos/neg/neutre × ledger → pertinence par signal/chemin → copy-lessons + amélioration + lookalike.
⛔ **Une boucle qu'il faut penser à lancer à la main ne tourne jamais** — or c'est LE différenciateur du flow (« il apprend de vos réponses »). Donc **juste après le launch, PROPOSER de la planifier**, ne pas se contenter de l'évoquer :
- **Si l'environnement du user permet les tâches planifiées** → proposer de créer la routine hebdo et la créer s'il accepte.
- **Sinon** → le dire clairement et convenir d'un rappel : « relancez `outbound-weekly` chaque lundi ». Ne jamais laisser croire que la boucle tournera toute seule si rien ne la déclenche.

Le prompt de la routine doit être **auto-suffisant** (chaque run démarre sans mémoire de la conversation) et contenir :
1. ⛔ **CHECK des connexions en étape 0** : appeler un tool léger de l'outil d'envoi → **si indisponible (run headless, auth expirée), prévenir le user et STOP**. Jamais de fallback, jamais d'analyse de mémoire.
2. Le **périmètre STRICT** (les campagnes du user uniquement, jamais l'inbox global), les identifiants de campagne/audience, et le rappel qu'elle **ANALYSE et PROPOSE** : elle n'envoie rien, ne lance rien, ne pousse aucun lead.
3. La **réserve statistique** : sur un petit volume → hypothèses, jamais de conclusions.

⛔ **Faire lancer la routine UNE FOIS à la main après l'avoir créée.** Les approbations de tools obtenues pendant un run sont mémorisées et rejouées aux runs suivants. Sans ce premier run manuel, une routine qui utilise un **connecteur distant (MCP)** se bloque sur une demande de permission que **personne ne verra passer** au petit matin : la boucle a l'air planifiée, et ne tourne jamais. Ce run à blanc vérifie aussi le garde-fou des connexions et le comportement à vide (aucune réponse encore = « pas assez de matière », surtout pas une tendance inventée).
**Timing** : lundi matin (bilan de la semaine écoulée).

## Garde-fous
Le flow PROPOSE et fait valider aux étapes sensibles (sourcing, copy, launch) ; il n'envoie jamais seul. Jamais de fausse perso.
