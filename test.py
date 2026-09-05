from core.transcriber import transcribe_all
from utils.audioprocessor import process_input


source = "https://www.youtube.com/watch?v=D24fAKfwpEs"

chunks = process_input(source)

print(transcribe_all(chunks))

