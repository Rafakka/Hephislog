
unit_map = {

    "xicara":"Xca",
    "xicaras":"Xcas",
    "chicara":"Xca",
    "chicaras":"Xcas",

    "cps":"Cps",
    "copos":"Cps",
    "copo":"Cp",

    "colher":"Cl",
    "colheres":"Cls",
    "colheres de sopa":"Cls Sopa",
    "colher de sopa":"Cl Sopa",
    "colher de sobremesa":"Cl SobreMs",
    "colheres de sobremesa":"Cls SobreMs",
    "colheres de cha":"Cls Chá",
    "colher de cha":"Cl Chá",

    "g": "g",
    "grama": "g",
    "gramas":"Grm",
    "gramos":"Grm",
    "gram":"Grm",
    "gms":"Grm",

    "kg": "kg",
    "kilos":"Kgs",
    "kilo":"Kg",
    "quilo":"Kg",
    "quilos":"Kgs",
    "unit":"Unit",

    "ml":"Ml",
    "mls":"Mls",
    "mililitro": "Ml",
    "mililitros": "Mls",
    
    "l": "ml",
    "litro": "ml",

    "pitada": "pt",
    "unidade": "Unit"

    }

UNICODE_FRACTIONS = {
    "½": 0.5,
    "¼": 0.25,
    "¾": 0.75,
    "⅓": 1/3,
    "⅔": 2/3,
    "⅛": 1/8,
}

def parse_ingredient_line(line: str) -> dict:
    """
    Parses an ingredient line like:
        "1 xícara de farinha de trigo"
        "1 1/2 colher (sopa) de óleo"
        "1 pitada de sal"
        "½ xícara (chá) de açúcar"
    Returns a dict with:
        {"quantity": float|None, "unit": str|None, "name": str, "notes": str|None}
    """

    original = line
    line = line.strip().lower()

    quantity = None
    unit = None
    notes = None

    # ---------------------------------------
    # 1) UNICODE FRACTIONS FIRST (½ ¼ ¾)
    # ---------------------------------------
    for uf, val in UNICODE_FRACTIONS.items():
        if line.startswith(uf):
            quantity = val
            line = line[len(uf):].strip()
            break

    # ---------------------------------------
    # 2) MIXED NUMBER: "1 1/2"
    # ---------------------------------------
    if quantity is None:
        mixed = re.match(r'^(\d+)\s+(\d+/\d+)', line)
        if mixed:
            whole = int(mixed.group(1))
            num, den = mixed.group(2).split('/')
            quantity = whole + (int(num) / int(den))
            line = line[mixed.end():].strip()

    # ---------------------------------------
    # 3) FRACTION ONLY: "3/4"
    # ---------------------------------------
    if quantity is None:
        frac = re.match(r'^(\d+/\d+)', line)
        if frac:
            num, den = frac.group(1).split('/')
            quantity = int(num) / int(den)
            line = line[frac.end():].strip()

    # ---------------------------------------
    # 4) DECIMAL OR INTEGER
    # ---------------------------------------
    if quantity is None:
        num_match = re.match(r'^(\d+[.,]?\d*)', line)
        if num_match:
            num_text = num_match.group(1).replace(',', '.')
            try:
                quantity = float(num_text)
            except ValueError:
                quantity = None
            line = line[num_match.end():].strip()

    # ---------------------------------------
    # 5) UNIT MATCHING (longest-first match)
    # ---------------------------------------
    for raw_unit in sorted(UNIT_MAP.keys(), key=len, reverse=True):
        if raw_unit in line:
            unit = UNIT_MAP[raw_unit]
            line = line.replace(raw_unit, "").strip()
            break

    # ---------------------------------------
    # 6) NOTES IN PARENTHESES
    # ---------------------------------------
    notes_match = re.search(r'\((.*?)\)', line)
    if notes_match:
        notes = notes_match.group(1).strip()
        line = re.sub(r'\(.*?\)', '', line).strip()

    # ---------------------------------------
    # 7) CLEAN NAME
    # ---------------------------------------
    name = line
    # remove "de " if it's a leftover
    if name.startswith("de "):
        name = name[3:].strip()

    name = name.strip().replace(" ,", ",").replace("  ", " ")

    # ---------------------------------------
    # 8) FINAL SAFETY
    # ---------------------------------------
    if not name:
        name = original.strip()

    return {
        "quantity": quantity,
        "unit": unit,
        "name": name,
        "notes": notes
    }
