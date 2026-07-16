#!/usr/bin/env python3
"""Gate mécanique sur un fichier de messages outbound.

Usage : python3 check-copy.py <fichier.md> [--expect N]
Exit 0 = pass, 1 = fail. Un gate se lance, il ne se déclare pas.

Les messages sont séparés par des titres markdown (## ...) ou, à défaut,
par des lignes vides. --expect N échoue si le découpage ne trouve pas les
N messages attendus : un gate qui analyse le mauvais nombre de messages
donne une assurance fausse, ce qui est pire que pas de gate du tout.
"""
import re
import sys
from collections import Counter

SEUIL_TEMPLATE = 0.30  # un n-gram partagé par plus de 30% des messages = squelette commun
TAILLE_NGRAM = 4

TICS = [
    "n'hésitez pas", "n'hesitez pas", "je me permets", "au plaisir",
    "en espérant", "en esperant", "je reviens vers vous", "j'espère que vous allez bien",
    "j'espere que vous allez bien", "dans l'attente", "bien à vous", "bien a vous",
    "je vous souhaite", "sans plus attendre", "il est important de",
]


def decouper(texte):
    blocs = re.split(r"^##+ .*$", texte, flags=re.MULTILINE)
    msgs = [b.strip() for b in blocs if b.strip()]
    if len(msgs) < 2:
        msgs = [b.strip() for b in re.split(r"\n\s*\n", texte) if b.strip()]
    # les lignes de commentaire (#) et de métadonnées ne sont pas du message
    nettoyes = []
    for m in msgs:
        lignes = [l for l in m.splitlines() if not l.lstrip().startswith("#")]
        lignes = [l for l in lignes if not re.match(r"^\s*(signal|lead|format|variable)\s*:", l, re.I)]
        if any(l.strip() for l in lignes):
            nettoyes.append("\n".join(lignes).strip())
    return nettoyes


def normaliser(msg):
    sans_var = re.sub(r"\{\{.*?\}\}|\(\(.*?\)\)", " ", msg)
    return re.sub(r"[^\w\s]", " ", sans_var.lower()).split()


def ngrams(mots, n):
    return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: check-copy.py <fichier.md> [--expect N]", file=sys.stderr)
        return 2
    attendu = None
    if "--expect" in sys.argv:
        try:
            attendu = int(sys.argv[sys.argv.index("--expect") + 1])
        except (IndexError, ValueError):
            print("FAIL : --expect attend un nombre", file=sys.stderr)
            return 2
    try:
        texte = open(args[0], encoding="utf-8").read()
    except OSError as e:
        print(f"FAIL lecture : {e}", file=sys.stderr)
        return 2

    msgs = decouper(texte)
    if not msgs:
        print("FAIL : aucun message trouvé dans le fichier")
        return 1

    # Un découpage raté fait analyser 1 bloc géant : les checks passent sans
    # rien tester. On refuse plutôt que de rendre un PASS qui ne prouve rien.
    if attendu is not None and len(msgs) != attendu:
        print(f"❌ FAIL découpage : {len(msgs)} message(s) détecté(s), {attendu} attendu(s).")
        print("   Sépare chaque message par un titre markdown « ## <lead> ».")
        print("   Un gate qui analyse le mauvais nombre de messages ne gate rien.")
        return 1
    if attendu is None and len(msgs) == 1 and len(texte) > 600:
        print("❌ FAIL découpage : 1 seul message détecté sur un fichier long.")
        print("   Sépare chaque message par un titre markdown « ## <lead> », ou passe --expect N.")
        return 1

    echecs = []

    # 1. em-dash : NO GO absolu
    for i, m in enumerate(msgs, 1):
        if "—" in m:
            echecs.append(f"message {i} : em-dash (—) interdit")

    # 2. tics de LLM
    for i, m in enumerate(msgs, 1):
        bas = m.lower()
        for tic in TICS:
            if tic in bas:
                echecs.append(f'message {i} : tic IA « {tic} »')

    # 3. squelette commun = template (le défaut que l'oeil ne voit pas)
    template_teste = len(msgs) >= 3
    if template_teste:
        compte = Counter()
        for m in msgs:
            for g in ngrams(normaliser(m), TAILLE_NGRAM):
                compte[g] += 1
        seuil = max(2, int(len(msgs) * SEUIL_TEMPLATE))
        communs = [(g, c) for g, c in compte.items() if c > seuil]
        communs.sort(key=lambda x: -x[1])
        for g, c in communs[:5]:
            pct = round(100 * c / len(msgs))
            echecs.append(f'TEMPLATE : « {g} » dans {c}/{len(msgs)} messages ({pct}%)')

    print(f"{len(msgs)} messages analysés.")
    if echecs:
        print(f"\n❌ FAIL ({len(echecs)} problèmes)\n")
        for e in echecs:
            print(f"  - {e}")
        print("\nUn message transposable est un template : on jette et on réécrit.")
        return 1

    if not template_teste:
        print("⚠️  PASS PARTIEL : 0 em-dash, 0 tic connu.")
        print(f"   Détection de template NON exécutée ({len(msgs)} message(s), il en faut 3).")
        print("   Ne pas lire ce résultat comme « aucun template » : rien n'a été testé.")
        return 0

    print("✅ PASS : 0 em-dash, 0 tic connu, aucun squelette commun détecté.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
