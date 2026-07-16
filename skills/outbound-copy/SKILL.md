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

## Étape 3 — MÉTHODE d'écriture (⛔ règles DURES, cause racine du template)
- ⛔ **JAMAIS écrire un message avec un script** (bash, python, boucle, template à trous, sed). Le message ne se GÉNÈRE pas, il s'ÉCRIT. Un script peut préparer/lire/aplatir les dossiers de leads, **jamais produire le texte d'un message**.
- ⛔ **UNE PASSE D'ÉCRITURE = UN LEAD.** Écrire N messages dans une seule passe produit mécaniquement N variantes du même message : le modèle s'auto-imite, le message 1 devient le patron des suivants. C'est LA cause racine du template (plus encore que le script).
- **Boucle obligatoire, quel que soit le mode** : pour chaque lead → relire SON dossier (signal, boîte, rôle, contexte) → écrire SON message → passer au suivant.
- **Volume par passe** : petits lots (~5 à 10 leads), **jamais 20+ d'un coup**. Au-delà, la qualité s'effondre par auto-imitation.

### Les 2 modes d'écriture — forces INÉGALES, le dire au user
⛔ **« Oublie le message précédent » NE MARCHE PAS** et ne doit jamais être proposé comme solution : un modèle **ne peut pas oublier ce qui est dans sa fenêtre** — les messages déjà écrits restent des tokens auxquels l'attention accède mécaniquement. La consigne pointe vers ce qu'elle interdit (« ne pense pas à un éléphant ») : au mieux elle réduit la copie littérale, elle **n'empêche pas le calage sur le patron** — le mécanisme le plus discret (cas vécu : 20 messages sans un seul copier-coller, tous bâtis sur le même squelette).

**MODE A — un sous-agent par lead (défaut recommandé, le plus fort)**
Chaque message est écrit par un sous-agent qui reçoit UNIQUEMENT : le **dossier COMPACT de SON lead** (la ligne digest de `outbound-enrich`, ~5 lignes max) + la voix du user + 2-3 exemples validés. ⛔ **JAMAIS le JSON brut d'enrichissement.** Il n'a jamais vu les autres messages → **le template est structurellement impossible**, pas juste déconseillé.
Il rend **le message seul** : pas de préambule, pas d'explication, pas de justification.
**Le coût du mode A n'est pas le nombre de sous-agents, c'est ce qu'on met dedans** : dossier compact + prompt court = un sous-agent par lead reste économique. C'est ce qui rend la perso par lead soutenable. Coût à annoncer et faire valider quand même : c'est ce que le user achète (chaque lead traité à la main).

**MODE B — fil direct + AUDIT ex post (économique, plus faible, honnête sur sa limite)**
En fil direct, l'auto-imitation est **inévitable** (voir ci-dessus). On ne l'empêche donc pas : **on la détecte et on réécrit**.
1. Écrire lead par lead en relisant SON dossier à chaque fois (jamais de script, jamais de passe groupée), sans relire les messages déjà écrits.
2. Lot terminé → **relire les messages CÔTE À CÔTE**. C'est le seul moment où les voir ensemble est utile : c'est ce qui rend le **squelette commun** visible (même ouverture, même pitch, même clôture).
3. Appliquer le test anti-template à chacun → tout message transposable est **jeté et réécrit**.
Le filet est **ex post** mais réel : il attrape ce qu'aucune consigne d'amnésie ne peut empêcher.

**Règle de présentation au user** : mode A = template impossible / plus cher. Mode B = template détectable et corrigé / moins cher. Ne JAMAIS les présenter comme équivalents.

## Étape 3bis — Écrire (règles DURES de contenu)
- **DM1 = ouverture + icebreaker + 2 phrases.** L'icebreaker porte sur le signal réel (de outbound-enrich), puis 2 phrases MAX. Le 1er message peut ne pas finir par une question.
- ⛔ **L'ouverture humaine n'est PAS systématique.** `hello {{firstname}} ça va ?` sur 20/20 messages n'est plus une touche humaine, c'est un tic — donc un template. La varier FORTEMENT d'un lead à l'autre, et parfois n'en mettre aucune.
- ⛔ **Le pitch ne peut PAS être identique d'un lead à l'autre.** Si le signal ne change que l'accroche et que la suite est commune, c'est de la fausse perso (déjà interdite) : le signal doit changer l'**ANGLE**, donc ce qu'on lui dit — pas juste l'entrée en matière. Signal = préfixe décoratif devant un pitch commun → à jeter.
- ⛔ **TEST ANTI-TEMPLATE (hard fail)** : prendre le message, changer le prénom, se demander « est-ce qu'il marche pour un autre lead du lot ? ». Si **OUI → c'est un template : on jette et on réécrit.** Un vrai message perso est **INTRANSPOSABLE** : il ne peut être envoyé qu'à cette personne-là.
- ⛔ **Zéro tic de LLM.** Les **tirets cadratins (—) sont un NO GO absolu** dans le copy. Traquer aussi : formulations trop propres, symboles inhabituels, structures parfaitement équilibrées, transitions léchées. **Un humain tape vite et imparfaitement** — le message doit en avoir l'air.
- ⛔ **Jamais de bêtise prix** : ne dire d'un produit qu'il est gratuit / freemium / « gratuit pour commencer » **que si le pricing capté à l'onboarding (`outbound-run` phase 0) le confirme pour la fonctionnalité citée**. Doute → aucune mention de prix.
- **Emails : TOUJOURS finir par la variable `{{signature}}`.** Jamais un prénom signé en dur.
- **Reformulation JAMAIS paraphrase** : ne jamais reprendre les faits/chiffres du profil de façon reconnaissable. Un humain ne recrache pas la fiche → parler de la réalité vécue du prospect sans réciter aucun data point.
- **Ne JAMAIS attaquer une force** du prospect (ex. multi-enrichissement = souvent mieux que simple). Pas d'angle sur une fausse faiblesse.
- **Imperfections humaines** dosées (~1 msg/2-3), VARIÉES, jamais dupliquées entre 2 messages (signature de template = grillé, le milieu est petit).
- **Varier les questions de clôture** ; une seule question "famille data/fichiers" par lot.
- **Pair-à-pair** : le background du user (son parcours, ses USP) crée la crédibilité.
- Relances : courtes, dans la voix, n'apportent que du neuf (jamais une redite du DM1 ; structure de séquence : `outbound-sequence`).

## Étape 4 — GATE (obligatoire avant push)
⛔ **Un gate se LANCE, il ne se DÉCLARE jamais.** Interdiction absolue d'écrire « ✓ », « check OK », « gate passé » sans avoir **exécuté la commande et lu son exit code dans le run courant**. Un gate auto-déclaré ne gate rien (cas vécu : « pas de em-dash ✓ » annoncé sur un fichier qui en contenait un). **Coller le résultat réel, jamais un résumé de mémoire.**
Sur le fichier de messages, avant tout push :
1. ⛔ **Check mécanique (premier, bloquant)** : `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check-copy.py" <fichier>` → **exit 0 obligatoire**. Détecte les em-dash, les tics de LLM connus, et le **TEMPLATE**. Ce script **remplace le `grep -n "—"` manuel** : il le fait, et davantage.
   **Le détecteur de template est mécanique** : un n-gram de 4 mots partagé par plus de 30 % des messages = squelette commun. Il attrape ce que ni l'œil ni l'agent qui a écrit ne voient (cas vécu : 20 messages sans un seul copier-coller, tous bâtis sur le même patron). S'il signale un n-gram partagé → **ces messages sont un template : on les réécrit, on ne discute pas le verdict.**
   ⚠️ **Format du fichier** : un message par titre `## <lead>` (à défaut, séparés par une ligne vide). Le script affiche « N messages analysés » → **vérifier que N = le nombre de leads du lot**. Si N vaut 1, le fichier est mal découpé et le détecteur de template ne teste RIEN (il lui faut ≥ 3 messages) : le PASS est alors vide de sens.
2. Relecture "humanize" (retirer le ton robotique, restaurer la cadence humaine) + traque des autres tics IA / formules interdites.
3. Un juge qui note la qualité en **contexte vierge** : un sous-agent dédié, jamais l'agent qui a écrit le message (un writer ne s'auto-note pas). Retry sur les défauts.
Checks à vérifier ensuite (pas à cocher de tête) : test anti-template passé sur CHAQUE message, `{{signature}}` en fin de chaque email, aucune affirmation de prix non vérifiée.

## Mapping attributs (sortie → outbound-push)
CA1 = message DM1 · CA3 = type de signal · CA4 = lien ressource (présent = branche B) · CA6 = langue. (CA2 icebreaker oral = INUTILE : le voice de l'outil d'envoi ne personnalise que le prénom.)
