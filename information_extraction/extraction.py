import json
import os
import re
from typing import Callable, Dict, Any, List, Tuple

from information_extraction.globals import CORPUS
from information_extraction.preprocessing import preprocess_pdf

"""
Function to extract different information from text.
Parameters:
    tasks - Any number of tuples (key, text, function):
        key - The key that will be applied for the value / result of the function in the generated JSON dictionary.
        text - The text to extract information from. Usually a specific article of the PDF to process, as the structure is mostly similar across samples.
        function - The extraction function to apply to the text. Should return a string or a dictionary.
"""
def extraction_pipeline(*tasks: Tuple[str, str, Callable[[str], Any]]) -> Dict[str, Any]:
    info = {}

    for key, text, function in tasks:
        info[key] = function(text)

    return info

"""
Template-based approach for extracting salary thresholds (umbrales) from a specific text. 
"""
def extract_umbrales(text):
    result = {
        "1": {},
        "2": {},
        "3": {}
    }

    umbrales = re.findall(r'\b\d{1,3}(?:\.\d{3})+\b', text)
    umbrales = [int(u.replace('.', '')) for u in umbrales]

    if len(umbrales) != 27:
        return "unknown"

    style = "bullet" if "•" in text else "table"

    if style == "bullet":
        for u in range(3):
            start = u * 9
            for i in range(8):
                result[str(u+1)][str(i+1)] = umbrales[start + i]
            result[str(u+1)]["8+"] = umbrales[start + 8]

    elif style == "table":
        for i in range(8):
            result["1"][str(i+1)] = umbrales[i*3]
            result["2"][str(i+1)] = umbrales[i*3 + 1]
            result["3"][str(i+1)] = umbrales[i*3 + 2]
        result["1"]["8+"] = umbrales[24]
        result["2"]["8+"] = umbrales[25]
        result["3"]["8+"] = umbrales[26]

    return result

def main():
    for filename in CORPUS:
        pdf = preprocess_pdf(filename)
        info = extraction_pipeline(
            ("umbrales", pdf["IV"]["articles"]["19"]["content"], extract_umbrales)
        )

        os.makedirs('information_extraction/results', exist_ok=True)
        with open(f'information_extraction/results/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

main()
