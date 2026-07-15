# derrick-outbound — ton agent de prospection autonome

Un agent qui fait ta prospection sortante de bout en bout, directement dans Claude Code :
il **trouve** tes prospects, les **enrichit**, écrit un **message perso à ta voix** (pas un template),
te prépare la **séquence**, puis **lit les réponses** chaque semaine pour s'améliorer et aller chercher
des profils qui ressemblent à ceux qui te répondent.

Deux briques : **Derrick** (la donnée B2B) + **ton outil d'envoi** (La Growth Machine aujourd'hui ; Lemlist et autres à venir ; sinon export CSV / API).

## Installation

```
/plugin install derrick-outbound@DerrickAppOrg/derrick-outbound-plugin
```

Débutant ? Passe par **Claude Cowork** → Customize → Add custom plugin.

## Ce qu'il te faut
- Un compte **Derrick** (plan Standard+ pour l'API/MCP) — le moteur de données. → https://derrick-app.com
- Un compte **La Growth Machine** (ou export CSV / API si tu utilises autre chose).
- Tu connectes tes propres clés au premier lancement (elles restent chez toi, jamais dans ce repo).

## Utilisation
Lance **`outbound-run`**. Un mini-onboarding te pose quelques questions (tes outils, ton ICP précis, ta voix —
il analyse ta façon d'écrire pour te ressembler —, tes signaux, tes exclusions), puis il déroule :
sourcing → enrichissement → messages → reco de séquence → préparation des leads. Tu valides à chaque étape
sensible ; **rien ne part sans toi**.

## Les skills
| Skill | Rôle |
|---|---|
| `outbound-run` | orchestrateur : onboarding + enchaîne le flow |
| `outbound-source` | trouve les prospects (5 chemins, choisit le plus pertinent) |
| `outbound-enrich` | enrichit entreprise + profil + signaux |
| `outbound-copy` | écrit les messages à ta voix |
| `outbound-sequence` | te recommande la structure de séquence |
| `outbound-push` | prépare les leads dans ton outil d'envoi |
| `outbound-weekly` | lit les réponses, apprend, va chercher des sosies |

## Principes
Données via Derrick en priorité, recherche web en secours. Le critère, c'est la **pertinence** des leads (pas
le volume brut). Chaque message est personnalisé pour de vrai, jamais un template déguisé. La boucle apprend
de tes réponses pour t'améliorer semaine après semaine.

---
Fait avec ❤️ par [Derrick](https://derrick-app.com).
