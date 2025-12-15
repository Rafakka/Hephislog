from hephis_core.schemas.music_schemas import ChordSheetSchema
from hephis_core.services.cleaners.data_cleaner import normalize_chords
from bs4 import BeautifulSoup
from hephis_core.infra.extractors.music.from_betty import extract_paragraphs_from_betty
import re

class ChordDetector:

    ROOTS = ChordSheetSchema.ROOTS
    QUALITIES = ChordSheetSchema.QUALITIES
    ACCIDENTALS = ChordSheetSchema.ACCIDENTALS

    _CHORD_RE = re.compile(
        r"""
        ^\s*
        [A-G]                # root
        (?:[#b])?            # accidental
        (?:                  # optional quality/extensions
            (?:
                m|maj|maj7|m7|7|sus|sus2|sus4|dim|aug|
                add9|add2|add11|6|9|11|13|°|ø
            )
            (?:\d*)?
            (?:\([^\)]*\))?
            (?:[^\s\/]*)?
        )?
        (?:\/[A-G](?:[#b])?)? # slash bass
        \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    _PAREN_REM = re.compile(r"\([^)]*\)")
    _MULTI_SPACE = re.compile(r"[ \t]{2,}")
    _SEP = re.compile(r"[\|,]+")

    ############# HELPERS ############################

    @staticmethod
    def is_root(token: str) -> bool:
        return bool(re.match(r"^[A-G](?:[#b])?$", token.strip(), re.IGNORECASE))

    @staticmethod
    def is_accidental(token: str) -> bool:
        return len(token) > 1 and token[1] in ("#", "b")

    @staticmethod
    def is_quality(token: str) -> bool:
        # a quick set membership test for known qualities (lowercase comparison)
        Qual = {"m","maj","maj7","m7","7","sus","sus2","sus4","dim","aug","add9","6","9","11","13","°","ø"}
        return token.strip().lower() in Qual

    @staticmethod
    def is_bass(token: str) -> bool:
        return bool(re.match(r"^[A-G](?:[#b])?$", token.strip(), re.IGNORECASE))


    ########## MAIN FUNCTIONS #########################################

    @staticmethod
    def is_main_chord(token: str) -> bool:
        clean_token = normalize_chords(token)

        if not clean_token:
            return False

        if not ChordDetector.is_root(clean_token[0]):
            return False

        if ChordDetector.is_accidental(clean_token):
            remainder = clean_token[2:]
        else:
            remainder = clean_token[1:]

        if not remainder:
            return True

        if ChordDetector.is_quality(remainder):
            return True

        return False
    
    @staticmethod
    def is_chord(token: str) -> bool:
        if not token or not isinstance(token, str):
            return False

        t = token.strip()
        t = ChordDetector._PAREN_REM.sub("", t).strip()
        t = re.sub(r"[,.;:\-]+$", "", t).strip()

        return bool(ChordDetector._CHORD_RE.match(t))

    @staticmethod
    def extract_chords_from_tokens(text: str) -> list[str]:
        """
        Extract chord-like tokens from a plain line.
        """
        if not text:
            return []

        s = str(text)

        s = ChordDetector._PAREN_REM.sub("", s)          # remove (3x)
        s = ChordDetector._SEP.sub(" ", s)               # replace , | with space
        s = re.sub(r"\s*-\s*", " ", s)     # turn dashes into separators
        s = ChordDetector._MULTI_SPACE.sub(" ", s).strip()

        tokens = [tok.strip() for tok in s.split() if tok.strip()]

        final = []
        for tok in tokens:
            if re.fullmatch(r"[-,.;:]+", tok):
                continue
            if ChordDetector.is_chord(tok):
                final.append(normalize_chords(tok))

        return final

    @staticmethod
    def looks_like_chord_line(text: str, min_ratio: float = 0.6) -> bool:
        """
        Optional helper if you want chord detection with ratio threshold.
        """
        if not text:
            return False

        s = ChordDetector._PAREN_REM.sub("", text)
        s = ChordDetector._SEP.sub(" ", s)
        s = re.sub(r"\s*-\s*", " ", s)

        tokens = [t for t in s.split() if t.strip()]
        if not tokens:
            return False

        chord_count = sum(1 for t in tokens if ChordDetector.is_chord(t))
        return (chord_count / len(tokens)) >= min_ratio

    @staticmethod
    def block_contains_chords(text:str) -> bool:
        lines = text.split("\n")
        for line in lines:
            if ChordDetector.looks_like_chord_line(line):
                return True
        return False

    @staticmethod
    def extract_chords_from_block(text:str) -> list[str]:
        chord_lines = []
        lines = text.split("\n")
        for line in lines:
            if ChordDetector.looks_like_chord_line(line):
                chord_lines.append(line)
        return chord_lines
    
    @staticmethod
    def detect_from_html(html: str) -> dict | None:
        # 1️⃣ Try site-specific helpers FIRST
        betty = extract_paragraphs_from_betty(html)
        if betty:
            return ChordDetector.detect_from_text(
                betty["text"],
                title=betty["title"],
                source="betty"
            )

        # 2️⃣ Generic HTML → text fallback
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)

        return ChordDetector.detect_from_text(text, source="html")
    
    @staticmethod
    def detect_from_text(text: str, title="Unknown Title", source="text") -> dict | None:

        if not text:
            return None

        lines = text.splitlines()

        chord_lines = [
            line for line in lines
            if ChordDetector.looks_like_chord_line(line)
        ]

        if not chord_lines:
            return None

        chords = []
        for line in chord_lines:
            chords.extend(ChordDetector.extract_chords_from_tokens(line))

        if not chords:
            return None

        return {
            "title": title,
            "chords": chords,
            "raw_lines": chord_lines,
            "source": source
        }
    
    @staticmethod
    def detect(data, input_type: str) -> dict | None:
        if input_type == "html":
            return ChordDetector.detect_from_html(data)
        if input_type == "text":
            return ChordDetector.detect_from_text(data)

        return None