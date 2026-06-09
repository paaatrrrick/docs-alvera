#!/usr/bin/env python3
"""Translate engineering-log MDX files English -> French.

Strategy: template-based regex substitution. The corpus is fictional incident
reports composed from a small, fixed set of sentence templates with a few
variable slots (station names, numbers, years, materials, weather conditions,
persons). All templates and slot vocabularies are hand-mapped to French.
"""

import os
import re
import sys

SRC = os.path.expanduser("~/workspace/misc/engineering-log")
DST = os.path.expanduser("~/workspace/fr/misc/engineering-log")

# ---------------------------------------------------------------------------
# Vocabularies
# ---------------------------------------------------------------------------

# Weather/condition phrases used in the "signal cable" sentence.
WEATHER_FR = {
    "a hailstorm that stripped the orchards": "un orage de grêle qui a dépouillé les vergers",
    "a long fog season": "une longue saison de brouillard",
    "a still and windless month": "un mois calme et sans vent",
    "an early frost": "une gelée précoce",
    "spring floods": "les crues de printemps",
    "the autumn king tides": "les grandes marées d'automne",
    "the dry easterlies": "les vents d'est secs",
    "weeks of sideways rain": "des semaines de pluie battante",
}

# Materials used to reseal the junction box. Translated as masculine nouns
# (the elided form follows "avec" which doesn't elide; agreement of the
# improvisation phrase stays feminine in French because "improvisation" is fem.).
MATERIAL_FR = {
    "blue slate": "de l'ardoise bleue",
    "bog iron": "du fer des marais",
    "fired clay": "de l'argile cuite",
    "hammered tin": "de l'étain martelé",
    "lacquered birch": "du bouleau laqué",
    "pressed kelp paper": "du papier de varech pressé",
    "river-glass": "du verre de rivière",
    "rope-fiber composite": "un composite de fibres de cordage",
    "salt-cured oak": "du chêne saumuré",
    "wax-sealed canvas": "de la toile cirée à la cire",
    "whale-bone veneer": "du placage en os de baleine",
    "woven reed": "du roseau tressé",
}

# ---------------------------------------------------------------------------
# Heading translations
# ---------------------------------------------------------------------------

HEADING_FR = {
    "## Summary": "## Résumé",
    "## Timeline": "## Chronologie",
    "## Investigation": "## Enquête",
    "## Root cause": "## Cause racine",
    "## Lessons and follow-up": "## Leçons apprises et suivi",
}

# ---------------------------------------------------------------------------
# Sentence templates: list of (compiled regex, french template)
# Each french template references named groups from the regex.
# ---------------------------------------------------------------------------

TEMPLATES = [
    # 1. Routine recalibration
    (
        re.compile(
            r"A routine recalibration at (?P<x>\w+) was performed against the wrong reference table, the one withdrawn in (?P<y>\d{4})\."
        ),
        "Un recalibrage de routine à {x} a été effectué d'après la mauvaise table de référence, celle retirée en {y}.",
    ),
    # 2. Pressure readings drift
    (
        re.compile(
            r"The pressure readings from the (?P<x>\w+) pumping station drifted upward for (?P<n>\d+) hours before anyone thought to distrust the gauge itself\."
        ),
        "Les relevés de pression de la station de pompage de {x} ont dérivé vers le haut pendant {n} heures avant que quiconque ne songe à se méfier de la jauge elle-même.",
    ),
    # 3. Relay tower stopped heartbeats
    (
        re.compile(
            r"At roughly (?P<h>\d+):40 in the morning, the relay tower at (?P<x>\w+) stopped acknowledging heartbeats, and the operators assumed the usual corroded contact\."
        ),
        "Vers {h}h40 du matin, la tour de relais de {x} a cessé d'accuser réception des battements, et les opérateurs ont supposé le contact corrodé habituel.",
    ),
    # 4. Signal cable shorted (weather condition)
    (
        re.compile(
            r"During (?P<cond>[^,]+), the signal cable along the towpath shorted intermittently, producing phantom readings that matched no known failure mode\."
        ),
        "Pendant {cond_fr}, le câble de signal le long du chemin de halage s'est mis en court-circuit par intermittence, produisant des relevés fantômes qui ne correspondaient à aucun mode de défaillance connu.",
    ),
    # 5. Night crew anomalies
    (
        re.compile(
            r"The night crew at (?P<x>\w+) logged (?P<n>\d+) separate anomalies and, following procedure, escalated none of them\."
        ),
        "L'équipe de nuit de {x} a consigné {n} anomalies distinctes et, conformément à la procédure, n'en a remonté aucune.",
    ),
    # 6. Interviews established procedure
    (
        re.compile(
            r"Interviews established that the procedure existed, was correct, was printed, and was pinned behind a cabinet where nobody had seen it for years\."
        ),
        "Les entretiens ont établi que la procédure existait, était correcte, était imprimée et était affichée derrière une armoire où personne ne l'avait vue depuis des années.",
    ),
    # 7. Cross-checking gauge
    (
        re.compile(
            r"Cross-checking the gauge against a portable reference took twenty minutes and should have happened (?P<n>\d+) days earlier\."
        ),
        "La vérification croisée de la jauge avec une référence portable a pris vingt minutes et aurait dû avoir lieu {n} jours plus tôt.",
    ),
    # 8. Junction box resealed
    (
        re.compile(
            r"Inspection revealed the junction box had been resealed with (?P<mat>[a-z\- ]+), an improvisation dating to a repair in (?P<y>\d{4}) that nobody documented\."
        ),
        "L'inspection a révélé que la boîte de jonction avait été rescellée avec {mat_fr}, une improvisation remontant à une réparation en {y} que personne n'avait documentée.",
    ),
    # 9. Maintenance log fault
    (
        re.compile(
            r"The maintenance log showed the same fault reported (?P<n>\d+) times over (?P<m>\d+) months, each time closed as resolved with no notes\."
        ),
        "Le journal de maintenance montrait que la même défaillance avait été signalée {n} fois sur {m} mois, chaque fois clôturée comme résolue sans note.",
    ),
    # 10. Traced fault to spare part
    (
        re.compile(
            r"(?P<p1>\w+) (?P<p2>\w+) traced the fault to a spare part cannibalized from the decommissioned (?P<x>\w+) line, subtly out of tolerance\."
        ),
        "{p1} {p2} a tracé la défaillance jusqu'à une pièce de rechange récupérée sur la ligne désaffectée de {x}, subtilement hors tolérance.",
    ),
    # 11. Reference tables consolidated
    (
        re.compile(
            r"The reference tables have been consolidated; the withdrawn editions were collected and, with some ceremony, burned\."
        ),
        "Les tables de référence ont été consolidées ; les éditions retirées ont été rassemblées et, avec une certaine solennité, brûlées.",
    ),
    # 12. Adopting a rule
    (
        re.compile(
            r"We are adopting a rule from the (?P<x>\w+) yards: any fault reported three times earns a named owner and a written theory\."
        ),
        "Nous adoptons une règle des ateliers de {x} : toute défaillance signalée trois fois se voit attribuer un responsable nommé et une théorie écrite.",
    ),
    # 13. Deeper failure organizational
    (
        re.compile(
            r"The deeper failure was organizational: the station treated recurring anomalies as weather rather than as signal\."
        ),
        "L'échec plus profond était organisationnel : la station traitait les anomalies récurrentes comme du temps qu'il fait plutôt que comme un signal.",
    ),
    # 14. Spare parts tags
    (
        re.compile(
            r"Spare parts now carry tags listing origin and tolerance, a practice (?P<p1>\w+) (?P<p2>\w+) has advocated since (?P<y>\d{4})\."
        ),
        "Les pièces de rechange portent désormais des étiquettes indiquant l'origine et la tolérance, une pratique que {p1} {p2} préconise depuis {y}.",
    ),
    # 15. Total downtime
    (
        re.compile(
            r"Total downtime came to (?P<n>\d+) hours, most of it spent debating whose responsibility the gauge was\."
        ),
        "Le temps d'arrêt total a atteint {n} heures, dont la majeure partie passée à débattre de qui était responsable de la jauge.",
    ),
]


def translate_sentence(eng: str) -> str | None:
    """Try every template; return French if one matches exactly, else None."""
    for rx, fr_tpl in TEMPLATES:
        m = rx.fullmatch(eng)
        if m:
            d = m.groupdict()
            # Resolve weather condition
            if "cond" in d and d["cond"] is not None:
                cond = d["cond"]
                if cond not in WEATHER_FR:
                    return None
                d["cond_fr"] = WEATHER_FR[cond]
            # Resolve material
            if "mat" in d and d["mat"] is not None:
                mat = d["mat"]
                if mat not in MATERIAL_FR:
                    return None
                d["mat_fr"] = MATERIAL_FR[mat]
            return fr_tpl.format(**d)
    return None


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

TITLE_RX = re.compile(
    r'^title: "Incident report: (?P<x>\w+) station, log (?P<n>\d+)"$'
)
DESC_RX = re.compile(
    r'^description: "Postmortem of an instrumentation failure at the (?P<x>\w+) pumping and relay station\."$'
)


def translate_frontmatter_line(line: str) -> str | None:
    m = TITLE_RX.match(line)
    if m:
        return f'title: "Rapport d\'incident : station de {m["x"]}, journal {m["n"]}"'
    m = DESC_RX.match(line)
    if m:
        return f'description: "Post-mortem d\'une défaillance d\'instrumentation à la station de pompage et de relais de {m["x"]}."'
    return None


# ---------------------------------------------------------------------------
# File-level processor
# ---------------------------------------------------------------------------

# A paragraph (Summary / Investigation / Root cause / Lessons) consists of
# multiple sentences joined by single spaces. We split on ". " but must
# preserve trailing periods.
SENT_SPLIT_RX = re.compile(r"(?<=\. )(?=[A-Z])")


def split_sentences(paragraph: str) -> list[str]:
    # Use a regex that splits AFTER ". " when followed by capital letter.
    # Simpler: split on ". " then re-append "." to all but last.
    parts = paragraph.split(". ")
    sentences = []
    for i, p in enumerate(parts):
        if i < len(parts) - 1:
            sentences.append(p + ".")
        else:
            sentences.append(p)
    return sentences


def translate_paragraph(paragraph: str, unmatched: list[str]) -> str:
    sents = split_sentences(paragraph.strip())
    out = []
    for s in sents:
        s = s.strip()
        if not s:
            continue
        fr = translate_sentence(s)
        if fr is None:
            unmatched.append(s)
            out.append(s)  # leave English in place; will fail verification
        else:
            out.append(fr)
    return " ".join(out)


def translate_bullet(line: str, unmatched: list[str]) -> str:
    # Form: "- <sentence>"
    assert line.startswith("- ")
    body = line[2:].strip()
    fr = translate_sentence(body)
    if fr is None:
        unmatched.append(body)
        return line
    return "- " + fr


def process_file(src_path: str, dst_path: str, unmatched: list[str]) -> None:
    with open(src_path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    out_lines = []
    in_frontmatter = False
    in_code = False
    fm_seen_open = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Frontmatter delimiter
        if line.strip() == "---":
            if not fm_seen_open:
                fm_seen_open = True
                in_frontmatter = True
                out_lines.append(line)
            elif in_frontmatter:
                in_frontmatter = False
                out_lines.append(line)
            else:
                # stray "---" — preserve
                out_lines.append(line)
            i += 1
            continue

        if in_frontmatter:
            fr = translate_frontmatter_line(line)
            if fr is not None:
                out_lines.append(fr)
            else:
                out_lines.append(line)
            i += 1
            continue

        # Code fences
        if line.startswith("```"):
            in_code = not in_code
            out_lines.append(line)
            i += 1
            continue
        if in_code:
            out_lines.append(line)
            i += 1
            continue

        # Headings
        stripped = line.rstrip()
        if stripped in HEADING_FR:
            out_lines.append(HEADING_FR[stripped])
            i += 1
            continue

        # Bullet list item
        if line.startswith("- "):
            out_lines.append(translate_bullet(line, unmatched))
            i += 1
            continue

        # Blank line
        if line.strip() == "":
            out_lines.append("")
            i += 1
            continue

        # Otherwise: a paragraph line (single line of prose).
        out_lines.append(translate_paragraph(line, unmatched))
        i += 1

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))


def main() -> int:
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".mdx"))
    unmatched: list[str] = []
    for name in files:
        src = os.path.join(SRC, name)
        dst = os.path.join(DST, name)
        process_file(src, dst, unmatched)

    print(f"Processed {len(files)} files.")
    if unmatched:
        # Dedupe & print first few
        uniq = sorted(set(unmatched))
        print(f"UNMATCHED sentences ({len(uniq)} unique):")
        for u in uniq[:30]:
            print("  ::", u)
        return 1
    print("All sentences matched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
