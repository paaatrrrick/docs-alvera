import os, re, glob, sys

SRC = os.path.expanduser("~/workspace/misc/cookbook")
DST = os.path.expanduser("~/workspace/fr/misc/cookbook")
os.makedirs(DST, exist_ok=True)

ADJ_FR = {
    "Bargehand":   "du batelier",
    "Cooper":      "du tonnelier",
    "Fenland":     "des marais",
    "Ferryman":    "du passeur",
    "Harbor":      "du port",
    "Lock-keeper": "de l'éclusier",
    "Quayside":    "du quai",
    "Towpath":     "du chemin de halage",
}

NOUN_FR = {
    "barley soup":   "soupe d'orge",
    "broth":         "bouillon",
    "dumplings":     "boulettes",
    "griddle cakes": "galettes",
    "pan loaf":      "pain à la poêle",
    "pickle pot":    "marmite de saumure",
    "smoked hash":   "hachis fumé",
    "stew":          "ragoût",
}

def title_noun(en_noun):
    fr = NOUN_FR[en_noun]
    return fr[0].upper() + fr[1:]

ITEM_FR = {
    "almanac reprints":      "réimpressions d'almanach",
    "clockwork gears":       "engrenages d'horlogerie",
    "copper wire":           "fil de cuivre",
    "dye cakes":             "pains de teinture",
    "fermented tea bricks":  "briques de thé fermenté",
    "glass floats":          "flotteurs en verre",
    "lamp oil":              "huile de lampe",
    "loom parts":            "pièces de métier à tisser",
    "preserved lemons":      "citrons confits",
    "spice tins":            "boîtes d'épices",
    "tar barrels":           "tonneaux de goudron",
    "wool bales":            "balles de laine",
}

WEATHER_FR = {
    "a hailstorm that stripped the orchards": "une grêle qui dépouilla les vergers",
    "a long fog season":                       "une longue saison de brouillard",
    "a still and windless month":              "un mois calme et sans vent",
    "an early frost":                          "une gelée précoce",
    "spring floods":                           "les crues de printemps",
    "the autumn king tides":                   "les grandes marées d'automne",
    "the dry easterlies":                      "les vents d'est secs",
    "weeks of sideways rain":                  "des semaines de pluie battante",
}

LID_FR = {
    "blue slate":             "ardoise bleue",
    "bog iron":               "fer des tourbières",
    "fired clay":             "argile cuite",
    "hammered tin":           "étain martelé",
    "lacquered birch":        "bouleau laqué",
    "pressed kelp paper":     "papier d'algue pressée",
    "river-glass":            "verre de rivière",
    "rope-fiber composite":   "composite de fibre de corde",
    "salt-cured oak":         "chêne saumuré",
    "wax-sealed canvas":      "toile cirée",
    "whale-bone veneer":      "placage en os de baleine",
    "woven reed":             "roseau tressé",
}

def fr_de(phrase):
    """Combine the preposition 'de' with a phrase, handling French elision/contraction."""
    if phrase.startswith("les "):
        return "des " + phrase[4:]
    if phrase.startswith("le "):
        return "du " + phrase[3:]
    if phrase.startswith("l'") or phrase[0:1] in "aeiouéèêâîïôûhAEIOU":
        return "d'" + phrase
    return "de " + phrase

def tr_title(t):
    m = re.match(r'^Recipe:\s+(\S+)\s+(.+)$', t)
    assert m, f"unmatched title: {t}"
    adj_en, noun_en = m.group(1), m.group(2)
    return f"Recette\u00a0: {title_noun(noun_en)} {ADJ_FR[adj_en]}"

def tr_description(d):
    m = re.match(r'^A traditional canal-country recipe for (\S+) (.+), with method and notes\.$', d)
    assert m, f"unmatched description: {d}"
    adj_en, noun_en = m.group(1), m.group(2)
    return f"Une recette traditionnelle du pays des canaux pour {NOUN_FR[noun_en]} {ADJ_FR[adj_en]}, avec méthode et notes."

NAME_RE = r"[A-Z][a-zé]+(?:\s[A-Z][a-zé]+)+"

def tr_about_sentence(s):
    m = re.match(rf'^This is the version served at the lock-keeper tavern in (\w+), written down by ({NAME_RE}) sometime around (\d+) and argued about ever since\.$', s)
    if m:
        place, name, year = m.group(1), m.group(2), m.group(3)
        return f"Voici la version servie à la taverne de l'éclusier à {place}, consignée par {name} vers {year} et discutée à n'en plus finir depuis."
    m = re.match(rf'^Every family in (\w+) claims their own variant; this one comes from the ({NAME_RE}) household and leans saltier than most\.$', s)
    if m:
        place, name = m.group(1), m.group(2)
        return f"Chaque famille de {place} revendique sa propre variante\u00a0; celle-ci vient de la maison {name} et tend à être plus salée que la plupart."
    m = re.match(r'^Barge cooks prize this dish because it needs one pot, tolerates (.+), and improves when reheated\.$', s)
    if m:
        weather = m.group(1)
        return f"Les cuisiniers des péniches apprécient ce plat parce qu'il ne demande qu'une marmite, supporte {WEATHER_FR[weather]} et s'améliore en réchauffant."
    m = re.match(r'^The dish dates to the embargo years, when (.+) was scarce and cooks in (\w+) learned to do without\.$', s)
    if m:
        item, place = m.group(1), m.group(2)
        return f"Le plat remonte aux années d'embargo, lorsque {ITEM_FR[item]} se faisai(en)t rares et que les cuisiniers de {place} apprirent à s'en passer."
    raise ValueError(f"unmatched about sentence: {s!r}")

def tr_ingredient(s):
    m = re.match(r'^Stock enough to cover, roughly (\d+) ladles\.$', s)
    if m:
        return f"Bouillon en quantité suffisante pour couvrir, environ {m.group(1)} louches."
    m = re.match(r'^(\d+) onions, sliced with patience\.$', s)
    if m:
        return f"{m.group(1)} oignons, émincés avec patience."
    if s == "Vinegar, salt, and a hard pepper, ground coarse.":
        return "Vinaigre, sel et un poivre dur, moulu gros."
    if s == "A knuckle of smoked fat, or what the larder offers.":
        return "Un morceau de gras fumé, ou ce que le garde-manger propose."
    m = re.match(r'^About (\d+) handfuls of (.+), the best you can argue your way into\.$', s)
    if m:
        n, item = m.group(1), m.group(2)
        return f"Environ {n} poignées de {ITEM_FR[item]}, les meilleur(e)s que vous puissiez obtenir à force d'arguments."
    m = re.match(r'^A strip of (.+) for the lid weight, by tradition only\.$', s)
    if m:
        return f"Une bande de {LID_FR[m.group(1)]} pour lester le couvercle, par tradition seulement."
    raise ValueError(f"unmatched ingredient: {s!r}")

def tr_method_sentence(s):
    m = re.match(r'^Begin by rendering the fat slowly over a low flame until the kitchen smells faintly of the quayside, about (\d+) minutes\.$', s)
    if m:
        return f"Commencez par faire fondre lentement la graisse à feu doux jusqu'à ce que la cuisine sente légèrement le quai, environ {m.group(1)} minutes."
    m = re.match(r'^Stir in the (.+) and let it toast against the bottom of the pot until it catches just slightly\.$', s)
    if m:
        return f"Incorporez {ITEM_FR[m.group(1)]} et laissez griller contre le fond de la marmite jusqu'à ce que ça accroche très légèrement."
    m = re.match(r'^Add the onions and a generous pinch of salt, and do not rush them; the cooks of (\w+) say hurried onions are a confession of bad character\.$', s)
    if m:
        return f"Ajoutez les oignons et une généreuse pincée de sel, et ne les pressez pas\u00a0; les cuisiniers de {m.group(1)} disent que des oignons brusqués sont l'aveu d'un mauvais caractère."
    if s == "Finish with vinegar off the heat, taste, and adjust with more conviction than caution.":
        return "Terminez avec du vinaigre hors du feu, goûtez et rectifiez avec plus de conviction que de prudence."
    m = re.match(r'^Cover and leave it alone for (\d+) minutes, resisting all temptation; lifting the lid is traditionally blamed for (.+)\.$', s)
    if m:
        n, weather = m.group(1), m.group(2)
        return f"Couvrez et laissez tranquille pendant {n} minutes, en résistant à toute tentation\u00a0; soulever le couvercle est traditionnellement tenu pour responsable {fr_de(WEATHER_FR[weather])}."
    if s == "Pour in the stock in three additions, letting each one fall quiet before the next.":
        return "Versez le bouillon en trois fois, en laissant chaque ajout retomber au calme avant le suivant."
    raise ValueError(f"unmatched method sentence: {s!r}")

def tr_note_sentence(s):
    m = re.match(rf'^If you cannot find the proper smoked variety, ({NAME_RE}) suggests any firm fish and an apology\.$', s)
    if m:
        return f"Si vous ne trouvez pas la variété fumée authentique, {m.group(1)} suggère n'importe quel poisson ferme et une excuse."
    m = re.match(r'^Serve with dense bread and pickles; in (\w+) it would be unthinkable without both\.$', s)
    if m:
        return f"Servez avec un pain dense et des cornichons\u00a0; à {m.group(1)}, ce serait impensable sans les deux."
    m = re.match(r'^A version made with (.+) exists in (\w+) and is, by treaty, never discussed here\.$', s)
    if m:
        item, place = m.group(1), m.group(2)
        return f"Une version préparée avec {ITEM_FR[item]} existe à {place} et, par traité, n'est jamais évoquée ici."
    m = re.match(r'^Leftovers keep for (\d+) days in a cool larder and are widely considered better on the second day\.$', s)
    if m:
        return f"Les restes se conservent {m.group(1)} jours dans un garde-manger frais et sont largement réputés meilleurs le deuxième jour."
    raise ValueError(f"unmatched note sentence: {s!r}")

HEAD_FR = {
    "## About this dish":       "## À propos de ce plat",
    "## Ingredients":           "## Ingrédients",
    "## Method":                "## Méthode",
    "## Notes from the galley": "## Notes de la cambuse",
    "## Serving":               "## Service",
}

SECTION_TRANSLATORS = {
    "## About this dish":       tr_about_sentence,
    "## Method":                tr_method_sentence,
    "## Notes from the galley": tr_note_sentence,
    "## Serving":               tr_note_sentence,
}

def split_sentences(paragraph):
    parts = re.split(r'(?<=\.)\s+(?=[A-Z])', paragraph.strip())
    return [p.strip() for p in parts if p.strip()]

def translate_file(path):
    text = open(path).read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    assert m, f"no frontmatter: {path}"
    fm, body = m.group(1), m.group(2)

    def fm_repl(line):
        m1 = re.match(r'^title:\s*"(.+)"\s*$', line)
        if m1:
            return f'title: "{tr_title(m1.group(1))}"'
        m2 = re.match(r'^description:\s*"(.+)"\s*$', line)
        if m2:
            return f'description: "{tr_description(m2.group(1))}"'
        return line
    fm_out = "\n".join(fm_repl(l) for l in fm.split("\n"))

    out_lines = []
    current_section = None
    for raw_line in body.split("\n"):
        line = raw_line.rstrip("\n")
        if line.startswith("## "):
            assert line in HEAD_FR, f"unknown heading: {line}"
            current_section = line
            out_lines.append(HEAD_FR[line])
            continue
        if line.strip() == "":
            out_lines.append("")
            continue
        if line.startswith("- "):
            assert current_section == "## Ingredients", f"bullet outside Ingredients: {line!r}"
            content = line[2:]
            out_lines.append("- " + tr_ingredient(content))
            continue
        translator = SECTION_TRANSLATORS.get(current_section)
        assert translator, f"prose outside known section in {path}: {current_section!r} :: {line!r}"
        sentences = split_sentences(line)
        translated = " ".join(translator(s) for s in sentences)
        out_lines.append(translated)

    return f"---\n{fm_out}\n---\n" + "\n".join(out_lines)

def main():
    files = sorted(glob.glob(os.path.join(SRC, "*.mdx")))
    print(f"Found {len(files)} files")
    fail = 0
    for f in files:
        try:
            translated = translate_file(f)
        except Exception as e:
            fail += 1
            print(f"FAIL {os.path.basename(f)}: {e}")
            if fail > 10: sys.exit(1)
            continue
        out_path = os.path.join(DST, os.path.basename(f))
        with open(out_path, "w") as g:
            g.write(translated)
    print(f"Wrote {len(files)-fail} files; {fail} failures")

if __name__ == "__main__":
    main()
