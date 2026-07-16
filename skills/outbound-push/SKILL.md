---
name: outbound-push
description: >-
  Pousse les leads outbound vers l'outil d'envoi (étape PUSH du flow) via Derrick. Mappe les attributs,
  applique le split A/B, et contrôle les URLs après le push. Déclencheurs : "pousse les leads",
  "envoie dans l'audience", ou appelée en fin de flow.
---

# Outbound push — PUSH (Derrick → outil d'envoi)

Tool : `push_to_lgm` (0 crédit, 10 custom attributes + champs standard). Appels **séquentiels**.

## Mapping attributs
CA1 = message DM1 perso · CA2 = (inutilisé, le voice de l'outil ne prend que le prénom) · CA3 = type de signal (pour le ledger) · CA4 = lien ressource → **présent = branche B / absent = branche A** (split au push, loggé) · CA6 = langue. + champs standard (firstname, lastname, companyName, jobTitle, linkedinUrl).

## Vérif post-push (obligatoire)
`get_audience_leads` → chaque lead a une `linkedinUrl` NON vide (bug connu : slug non-ASCII/emoji → URL vide). Signaler toute URL vide.

## Dédup + log
Avant push : checker `leads.jsonl` (déjà contacté ?). Après : écrire chaque lead dans `leads.jsonl` (variant, signalType, sourcePath, status) pour la boucle d'apprentissage.

## Sortie
Leads dans l'audience du user (prêts pour le launch manuel), registres à jour.
