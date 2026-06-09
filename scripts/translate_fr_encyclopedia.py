#!/usr/bin/env python3
"""Translate the canal-trade encyclopedia from English to French."""
import os, re, sys, glob

SRC = os.path.expanduser("~/workspace/misc/encyclopedia")
DST = os.path.expanduser("~/workspace/fr/misc/encyclopedia")
os.makedirs(DST, exist_ok=True)

# ----- Vocabularies -----

# Nouns with French + gender (m / f)
NOUN_FR = {
    "arm":     ("bras",      "m"),
    "clock":   ("horloge",   "f"),
    "drum":    ("tambour",   "m"),
    "frame":   ("cadre",     "m"),
    "gate":    ("vanne",     "f"),
    "lantern": ("lanterne",  "f"),
    "scale":   ("balance",   "f"),
    "whistle": ("sifflet",   "m"),
}

# Activity adjective in English -> French verb (used as "à VERB")
ADJ_FR = {
    "counting":    "compter",
    "gauging":     "jauger",
    "leveling":    "niveler",
    "measuring":   "mesurer",
    "registering": "enregistrer",
    "sealing":     "sceller",
    "signaling":   "signaler",
    "sounding":    "sonder",
}

def starts_with_vowel(s):
    return s[0].lower() in "aeiouhâêîôûéèàù"

def device_noun_phrase(adj, noun):
    """Return tuple (article, head) where article is 'le '|'la '|"l'" and head is the rest.

    Example: ('le ', 'bras à compter')  /  ("l'", 'horloge à mesurer')
    """
    noun_fr, gender = NOUN_FR[noun]
    head = f"{noun_fr} à {ADJ_FR[adj]}"
    if starts_with_vowel(noun_fr):
        return ("l'", head)
    return (("le " if gender == "m" else "la "), head)

def device_phrase_cap(adj, noun):
    art, head = device_noun_phrase(adj, noun)
    return art[0].upper() + art[1:] + head

def device_phrase_de(adj, noun):
    """Contracted preposition: 'du'/'de la'/"de l'" + head."""
    art, head = device_noun_phrase(adj, noun)
    if art == "le ":
        return "du " + head
    if art == "la ":
        return "de la " + head
    # art == "l'"
    return "de l'" + head

# Cargo translations
CARGO_FR = {
    "almanac reprints":     "réimpressions d'almanachs",
    "clockwork gears":      "engrenages d'horlogerie",
    "copper wire":          "fil de cuivre",
    "dye cakes":            "pains de teinture",
    "fermented tea bricks": "briques de thé fermenté",
    "glass floats":         "flotteurs de verre",
    "lamp oil":             "huile à lampe",
    "loom parts":           "pièces de métier à tisser",
    "preserved lemons":     "citrons confits",
    "spice tins":           "boîtes d'épices",
    "tar barrels":          "tonneaux de goudron",
    "wool bales":           "balles de laine",
}

# Cargoes are countable plurals after "les"; for "huile à lampe" (mass) we use "l'"
def cargo_article(cargo_fr):
    """Return the article 'les ' or "l'" or 'la ' to use before the cargo for 'disputes over X' / 'measuring X fairly'."""
    if cargo_fr == "huile à lampe":
        return "l'"
    return "les "

UNIT_FR = {
    "bales":   "balles",
    "barrels": "tonneaux",
    "crates":  "caisses",
    "tins":    "boîtes",
}

MATERIAL_FR = {
    "blue slate":           "ardoise bleue",
    "bog iron":             "fer des marais",
    "fired clay":           "argile cuite",
    "hammered tin":         "étain martelé",
    "lacquered birch":      "bouleau laqué",
    "pressed kelp paper":   "papier d'algues pressées",
    "river-glass":          "verre de rivière",
    "rope-fiber composite": "composite de fibres de corde",
    "salt-cured oak":       "chêne saumuré",
    "wax-sealed canvas":    "toile cirée",
    "whale-bone veneer":    "placage en os de baleine",
    "woven reed":           "roseau tressé",
}

# Maker descriptor adjectives — masculine form (modifies "fabricant")
ADJ_MAKER_FR = {
    "ambitious":      "ambitieux",
    "celebrated":     "célèbre",
    "meticulous":     "méticuleux",
    "patient":        "patient",
    "prosperous":     "prospère",
    "quiet":          "discret",
    "reclusive":      "reclus",
    "restless":       "infatigable",
    "rowdy":          "turbulent",
    "stubborn":       "obstiné",
    "half-forgotten": "à demi oublié",
    "wind-bitten":    "tanné par le vent",
}

HEADINGS = {
    "## Origin": "## Origine",
    "## Design and operation": "## Conception et fonctionnement",
    "## Regional variants": "## Variantes régionales",
    "## Legacy": "## Postérité",
    "## Further reading": "## Pour aller plus loin",
}

TABLE_HEADER = "| Town | Calibrated for | Surviving examples |"
TABLE_HEADER_FR = "| Ville | Étalonné pour | Exemplaires subsistants |"
TABLE_SEP = "| --- | --- | --- |"

unmatched_sentences = {}

def translate_sentence(s):
    s_clean = s.strip()

    # 1
    m = re.match(r"^The device first appears in the customs inventories of (\w+) in (\d{4}), listed without explanation between rope and candles\.$", s_clean)
    if m:
        town, year = m.group(1), m.group(2)
        return f"L'appareil apparaît pour la première fois dans les inventaires douaniers de {town} en {year}, mentionné sans explication entre les cordages et les chandelles."

    # 2
    m = re.match(r"^Credit is usually given to ([A-Z][\w'-]+(?: [A-Z][\w'-]+)+), an? ([\w-]+) instrument maker of (\w+), though earlier sketches exist in the (\w+) archive\.$", s_clean)
    if m:
        name, adj, town, arch = m.group(1), m.group(2), m.group(3), m.group(4)
        adj_fr = ADJ_MAKER_FR.get(adj)
        if adj_fr is None:
            return None
        return f"On en attribue généralement le mérite à {name}, fabricant d'instruments {adj_fr} de {town}, bien que des esquisses antérieures existent dans les archives de {arch}."

    # 3
    m = re.match(r"^It was developed to solve a specific problem: measuring ([\w ]+) fairly when every town along the canal used different barrels\.$", s_clean)
    if m:
        cargo = m.group(1)
        cargo_fr = CARGO_FR.get(cargo)
        if cargo_fr is None:
            return None
        art = cargo_article(cargo_fr)
        return f"Il fut mis au point pour résoudre un problème précis : mesurer équitablement {art}{cargo_fr} alors que chaque ville le long du canal utilisait des tonneaux différents."

    # 4
    m = re.match(r"^The earliest surviving example is built of ([\w -]+) and brass, and still functions, to the mild annoyance of modern replicators\.$", s_clean)
    if m:
        mat = m.group(1)
        mat_fr = MATERIAL_FR.get(mat)
        if mat_fr is None:
            return None
        return f"Le plus ancien exemplaire conservé est fait de {mat_fr} et de laiton, et fonctionne encore, au léger agacement des reproducteurs modernes."

    # 5
    m = re.match(r"^The mechanism rests on a balanced arm of ([\w -]+), counterweighted so that a full measure tips it past the catch\.$", s_clean)
    if m:
        mat = m.group(1)
        mat_fr = MATERIAL_FR.get(mat)
        if mat_fr is None:
            return None
        return f"Le mécanisme repose sur un bras équilibré en {mat_fr}, contrebalancé de sorte qu'une mesure pleine le fait basculer au-delà du cliquet."

    # 6
    m = re.match(r"^Versions differ mainly in the throat width, which towns guarded jealously; (\w+) calibrated theirs in secret, at night\.$", s_clean)
    if m:
        town = m.group(1)
        return f"Les versions diffèrent surtout par la largeur du goulot, que les villes gardaient jalousement ; {town} étalonnait la sienne en secret, de nuit."

    # 7
    if s_clean == "The whole apparatus disassembles into a case the size of a bread loaf, which is why inspectors came to carry them everywhere.":
        return "L'appareil entier se démonte dans un étui de la taille d'un pain, ce qui explique pourquoi les inspecteurs en vinrent à les transporter partout."

    # 8
    m = re.match(r"^A clever escapement, added by ([A-Z][\w'-]+(?: [A-Z][\w'-]+)+) around (\d{4}), lets the operator read the result without stopping the flow\.$", s_clean)
    if m:
        name, year = m.group(1), m.group(2)
        return f"Un ingénieux échappement, ajouté par {name} vers {year}, permet à l'opérateur de lire le résultat sans interrompre le flux."

    # 9
    m = re.match(r"^By (\d{4}) it was standard equipment on every barge over a certain tonnage, and disputes over ([\w ]+) fell sharply\.$", s_clean)
    if m:
        year, cargo = m.group(1), m.group(2)
        cargo_fr = CARGO_FR.get(cargo)
        if cargo_fr is None:
            return None
        art = cargo_article(cargo_fr)
        # "les litiges au sujet des X" — when X starts with article "les " replace "des " naturally
        if art == "les ":
            connector = "des "
        elif art == "l'":
            connector = "de l'"
        else:
            connector = "de la "
        cargo_phrase = connector + cargo_fr
        return f"Dès {year}, il faisait partie de l'équipement standard de toute péniche dépassant un certain tonnage, et les litiges au sujet {cargo_phrase} chutèrent fortement."

    # 10
    m = re.match(r"^A working specimen is demonstrated on market days at the (\w+) museum by ([A-Z][\w'-]+(?: [A-Z][\w'-]+)+), who repairs them by feel\.$", s_clean)
    if m:
        town, name = m.group(1), m.group(2)
        return f"Un spécimen en état de marche est présenté les jours de marché au musée de {town} par {name}, qui les répare au toucher."

    # 11
    if s_clean == "The phrase tipping the arm survives in canal slang, meaning to settle an argument with evidence.":
        return "L'expression « faire basculer le bras » subsiste dans l'argot des canaliers, au sens de trancher une dispute par les preuves."

    # 12
    m = re.match(r"^Collectors now pay handsomely for examples with the (\w+) stamp, most of which are forgeries from (\w+)\.$", s_clean)
    if m:
        arch, town = m.group(1), m.group(2)
        return f"Les collectionneurs paient aujourd'hui de fortes sommes pour les exemplaires portant le poinçon de {arch}, dont la plupart sont des contrefaçons venues de {town}."

    return None

def translate_title(line):
    m = re.match(r'^title: "The (\w+) (\w+) of (\w+)"$', line)
    if m:
        adj, noun, town = m.group(1), m.group(2), m.group(3)
        phrase = device_phrase_cap(adj, noun)
        return f'title: "{phrase} de {town}"'
    return None

def translate_description(line):
    m = re.match(r'^description: "Origin, design, and legacy of the (\w+) (\w+) of (\w+), a fixture of canal trade\."$', line)
    if m:
        adj, noun, town = m.group(1), m.group(2), m.group(3)
        de_phrase = device_phrase_de(adj, noun)
        return f'description: "Origines, conception et postérité {de_phrase} de {town}, élément incontournable du commerce sur les canaux."'
    return None

def translate_table_row(line):
    m = re.match(r'^\| (\w+) \| ([\w ]+) \| (\d+) (\w+) \|$', line)
    if m:
        town, cargo, n, unit = m.group(1), m.group(2), m.group(3), m.group(4)
        cargo_fr = CARGO_FR.get(cargo, cargo)
        unit_fr = UNIT_FR.get(unit, unit)
        return f"| {town} | {cargo_fr} | {n} {unit_fr} |"
    return None

def split_sentences(paragraph):
    parts = re.findall(r'[^.]*\.(?:\s+|$)', paragraph)
    if "".join(parts).rstrip() != paragraph.rstrip():
        return None
    return parts

def translate_paragraph(p):
    parts = split_sentences(p)
    if parts is None:
        return None
    out = []
    for part in parts:
        stripped = part.rstrip()
        trailing = part[len(stripped):]
        tr = translate_sentence(stripped)
        if tr is None:
            unmatched_sentences[stripped] = unmatched_sentences.get(stripped, 0) + 1
            return None
        out.append(tr + trailing)
    return "".join(out).rstrip()

def translate_bullet(line):
    if not line.startswith("- "):
        return None
    body = line[2:]
    tr = translate_sentence(body)
    if tr is None:
        unmatched_sentences[body] = unmatched_sentences.get(body, 0) + 1
        return None
    return "- " + tr

def translate_file(path):
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    out = []
    i = 0
    in_frontmatter = False
    while i < len(lines):
        line = lines[i]

        if line == "---" and i == 0:
            out.append(line); in_frontmatter = True; i += 1; continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
                out.append(line); i += 1; continue
            if line.startswith("title:"):
                tr = translate_title(line)
                if tr is None:
                    print(f"  UNMATCHED TITLE in {path}: {line}", file=sys.stderr)
                    return None
                out.append(tr); i += 1; continue
            if line.startswith("description:"):
                tr = translate_description(line)
                if tr is None:
                    print(f"  UNMATCHED DESC in {path}: {line}", file=sys.stderr)
                    return None
                out.append(tr); i += 1; continue
            out.append(line); i += 1; continue

        if line in HEADINGS:
            out.append(HEADINGS[line]); i += 1; continue

        if line == TABLE_HEADER:
            out.append(TABLE_HEADER_FR); i += 1; continue
        if line == TABLE_SEP:
            out.append(TABLE_SEP); i += 1; continue
        if line.startswith("| ") and line.endswith(" |") and "---" not in line and "Town" not in line:
            tr = translate_table_row(line)
            if tr is not None:
                out.append(tr); i += 1; continue

        if line.startswith("- "):
            tr = translate_bullet(line)
            if tr is None:
                print(f"  UNMATCHED BULLET in {path}: {line[:140]}", file=sys.stderr)
                return None
            out.append(tr); i += 1; continue

        if line.strip() == "":
            out.append(line); i += 1; continue

        tr = translate_paragraph(line)
        if tr is None:
            print(f"  UNMATCHED PARA in {path}: {line[:160]}", file=sys.stderr)
            return None
        out.append(tr); i += 1

    return "\n".join(out)

# Pre-scan to discover any unseen "a X instrument maker" adjectives
seen_unknown = set()
for path in glob.glob(os.path.join(SRC, "*.mdx")):
    for adj in re.findall(r'an? ([\w-]+) instrument maker', open(path).read()):
        if adj not in ADJ_MAKER_FR and adj not in seen_unknown:
            seen_unknown.add(adj)
            print(f"  NOTE: unknown maker adj '{adj}'", file=sys.stderr)

files = sorted(glob.glob(os.path.join(SRC, "*.mdx")))
print(f"Found {len(files)} source files")
ok = 0; fail = 0
for path in files:
    result = translate_file(path)
    if result is None:
        fail += 1
        continue
    out_path = os.path.join(DST, os.path.basename(path))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)
    ok += 1

print(f"Translated OK: {ok}")
print(f"Failed:        {fail}")
if unmatched_sentences:
    print(f"\n--- Unmatched sentences ({len(unmatched_sentences)} unique) ---")
    for s, c in sorted(unmatched_sentences.items(), key=lambda x: -x[1])[:30]:
        print(f"  [{c}x] {s[:200]}")
