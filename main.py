from information_extraction import extraction
from summarisation import evaluation, generation

def main():
    extraction.main()
    generation.main()
    evaluation.main()

if __name__ == "__main__":
    main()