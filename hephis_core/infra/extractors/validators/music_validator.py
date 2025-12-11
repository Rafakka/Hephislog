

def is_valid_music(raw):
        return (
            isinstance(raw, dict)
            and "paragraphs" in raw
            and "title" in raw
        )