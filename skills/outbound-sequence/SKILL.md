---
name: outbound-sequence
description: >-
  Recommande la structure de séquence outbound (étape SÉQUENCE du flow). NE manipule PAS l'outil d'envoi :
  elle CONSEILLE dans le chat (canal, nombre de messages, espacement, branches) et livre le contenu bloc par
  bloc ; le user monte la séquence lui-même dans son outil (Lemlist / autre outil d'envoi). Déclencheurs :
  "monte la séquence", "structure la campagne", ou appelée dans le flow.
---

# Outbound sequence — SÉQUENCE (skill de RECO, pas de manipulation)

Cette skill **recommande dans le chat**, le user applique. Donc aucune dépendance à un tool "create campaign".

## Étape 1 — Reco de structure (adaptée au user)
Poser / déduire : **canal** (LinkedIn only / email only / multicanal), **nb de messages**, **espacement**. Recommander une structure par défaut éprouvée :
- Visite profil → invite (sans note) → DM1 (perso).
- Branche **Has Attribute (CA4)** : Yes = Voice + DM avec lien ressource (démo/meta-pitch) ; No = DM relance classique. Convergence → DM final.
- Bascule email 1 : invite non acceptée après 7j → 3 mails froids (le lead n'a rien vu).
- Bascule email 2 : connecté mais DM sans réponse → 3 mails qui référencent les DM.
Adapter selon l'outil du user et son ICP (ex. cible corporate → plus d'email ; founders → LinkedIn-first).

## Étape 2 — Livrer le contenu bloc par bloc
Donner, pour CHAQUE bloc nommé, le contenu exact à coller + quelles variables insérer (prénom, custom attributes). DM1 = variable message perso seule. Voice = "Bonjour {prénom}" (auto) + enregistrement commun (l'outil ne personnalise que le prénom). Relances = courtes, dans la voix du user, n'apportent que du neuf (écrites par `outbound-copy`).

## Étape 3 — Vérifs à faire faire au user
- Le "Has Attribute" branche bien Yes→Voice, No→relance.
- Le voice + le DM avec lien ressource sont sur la branche B (sinon lien vide chez les A).
- Renommer clairement chaque bloc.
- Attacher l'audience + lancer (le launch reste une action manuelle du user).

## Sortie
Un guide de montage clair (structure + contenu bloc par bloc + checklist de vérif). Aucun appel à l'outil d'envoi.
