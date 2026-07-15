---
name: outbound-push
description: >-
  Pousse les leads outbound vers l'outil d'envoi (étape PUSH du flow) via Derrick, avec le check pré-push
  anti-collision. Mappe les attributs, applique le split A/B, vérifie AVANT d'écrire qu'on n'écrase pas les
  données d'un lead déjà en campagne active, et contrôle les URLs après. Déclencheurs : "pousse les leads",
  "envoie dans l'audience", ou appelée en fin de flow.
---

# Outbound push — PUSH (Derrick → outil d'envoi)

Tool : `push_to_lgm` (0 crédit, 10 custom attributes + champs standard). Appels **séquentiels**.

## Mapping attributs
CA1 = message DM1 perso · CA2 = (inutilisé, le voice de l'outil ne prend que le prénom) · CA3 = type de signal (pour le ledger) · CA4 = lien ressource → **présent = branche B / absent = branche A** (split au push, loggé) · CA6 = langue. + champs standard (firstname, lastname, companyName, jobTitle, linkedinUrl).

## ⛔ Check pré-push ANTI-COLLISION en 2 passes (règle dure)
Le push écrit les custom attributes au niveau du **lead global partagé** → risque d'écraser ceux d'une campagne active d'un autre membre du workspace. Pas de "lookup lead by URL" ni de "remove lead" côté MCP → procédure :
1. **Passe détection** : push léger (linkedinUrl + nom SEULEMENT, zéro CA) dans une audience TAMPON → `get_audience_leads` → préexistants = `status != unknown` / id ancien / `proEmail` déjà rempli.
2. **Passe verdict** : pour chaque préexistant → `get_lead_logs` → ses `campaignId` → `list_campaigns` : une **RUNNING/READY** ? Si OUI → **exclu** (jamais de CA poussé = zéro écrasement, loggé dans removed.jsonl). Si inactives / lead neuf → **clean** → push AVEC les CA dans l'audience de campagne.
(La passe 1 sans CA est safe : le MCP filtre les valeurs vides, ne touche pas les CA existants.)

## Vérif post-push (obligatoire)
`get_audience_leads` → chaque lead a une `linkedinUrl` NON vide (bug connu : slug non-ASCII/emoji → URL vide). Signaler toute URL vide.

## Dédup + log
Avant push : checker `leads.jsonl` (déjà contacté ?). Après : écrire chaque lead dans `leads.jsonl` (variant, signalType, sourcePath, status) pour la boucle d'apprentissage.

## Sortie
Leads dans l'audience du user (prêts pour le launch manuel), registres à jour, collisions écartées et loggées.
