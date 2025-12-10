

def is_valid_music(self, raw):
            return (
                isinstance(raw, dict)
                and "paragraphs" in raw
                and "title" in raw
            )