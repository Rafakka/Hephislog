from hephis_core.services.detectors.chord_detector import(
    block_contains_chords, extract_chords_from_block
)
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action

@log_action(action="extract_music_from_text")
@extractor(domain="music", input_type="text")
def extract_music_from_text(text:str) -> dict | None:
    
    if not isinstance(text,str):
        return None
    
    lines = text.split("\n")
    
    chord_blocks=[]
    current_block=[]

    for line in lines:
        if block_contains_chords(line):
            current_block.append(line)
        else:
            if current_block:
                chord_blocks.append("\n".join(current_block))
            
    if current_block:
        chord_blocks.append("\n".join(current_block))
    
    if not chord_blocks:
        return None
    
    paragraphs = [
        extract_chords_from_block(block)
        for block in chord_blocks
    ]

    return {
        "title":"Unknown Title",
        "paragraphs":paragraphs,
        "source":"text_raw"
    }