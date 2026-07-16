---
name: outbound-sequence
description: >-
  Recommande la structure de séquence outbound (étape SÉQUENCE du flow). NE manipule PAS l'outil d'envoi :
  elle CONSEILLE dans le chat (canal, nombre de messages, espacement, branches) et livre le contenu bloc par
  bloc ; le user monte la séquence lui-même dans son outil (La Growth Machine / Lemlist / autre). Déclencheurs :
  "monte la séquence", "structure la campagne", ou appelée dans le flow.
---

# Outbound sequence — SÉQUENCE (skill de RECO, pas de manipulation)

Cette skill **recommande dans le chat**, le user applique. Donc aucune dépendance à un tool "create campaign".

## ⛔ Invite AVEC ou SANS note — les vrais chiffres (correction factuelle)
**Il est FAUX de dire « invite sans note car le taux d'acceptation est meilleur ».** Données réelles (étude Belkins, 20 millions d'invitations LinkedIn, 2024) :
- **Acceptation** : avec note personnalisée **26,42 %** · sans note **26,37 %** → **0,05 point d'écart : la note ne change RIEN à l'acceptation.**
- **Réponse** : **9,36 %** avec un message pertinent vs **5,44 %** sans → **+72 % de conversations.**
- Donc : la note ne sert pas à **passer la porte**, elle sert à **démarrer la conversation**. Le seul avantage du « sans note » = on avance plus vite dans la séquence.

3 règles à graver :
- (a) **La note n'est JAMAIS un pitch.** Une offre, une démo ou un lien de rdv dedans = grillé comme vendeur avant même d'être connecté.
- (b) **Le premier message donne une vraie raison, actuelle, sur EUX** — pas « voici comment on aide les boîtes comme la vôtre ».
- (c) **On compte les réponses, pas les connexions.** Une acceptation n'est pas une réponse ; une connexion n'est pas un lead.

**Présenter le choix au user avec ces chiffres** et le laisser trancher en connaissance de cause (note = plus de conversations ; sans note = séquence plus rapide).

## Étape 1 — Reco de structure (adaptée au user)
Poser / déduire : **canal** (LinkedIn only / email only / multicanal), **nb de messages**, **espacement**, **note d'invite ou non** (voir ci-dessus). Recommander une structure par défaut éprouvée :
- Visite profil → invite (note ou non, au choix du user) → DM1 (perso).
- Branche **Has Attribute (CA4)** : Yes = Voice + DM avec lien ressource (démo/meta-pitch) ; No = DM relance classique. Convergence → DM final.
- Bascule email 1 : invite non acceptée après 7j → 3 mails froids (le lead n'a rien vu).
- Bascule email 2 : connecté mais DM sans réponse → 3 mails qui référencent les DM.
Adapter selon l'outil du user et son ICP (ex. cible corporate → plus d'email ; founders → LinkedIn-first).

## Étape 2 — Livrer le contenu bloc par bloc
Donner, pour CHAQUE bloc nommé, le contenu exact à coller + quelles variables insérer (prénom, custom attributes). DM1 = variable message perso seule. Voice = "Bonjour {prénom}" (auto) + enregistrement commun (l'outil ne personnalise que le prénom). Relances = courtes, dans la voix du user, n'apportent que du neuf (écrites par `outbound-copy`). Tout bloc **email** se termine par `{{signature}}` (jamais un prénom en dur). Si le user choisit l'invite avec note : la note = 1 phrase sur EUX, **sans pitch ni lien**.

## Étape 3 — Vérifs à faire faire au user
- Le "Has Attribute" branche bien Yes→Voice, No→relance.
- Le voice + le DM avec lien ressource sont sur la branche B (sinon lien vide chez les A).
- Renommer clairement chaque bloc.
- Attacher l'audience + lancer (le launch reste une action manuelle du user).

## Sortie
Un guide de montage clair (structure + contenu bloc par bloc + checklist de vérif). Aucun appel à l'outil d'envoi.
