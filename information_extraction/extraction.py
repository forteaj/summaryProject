import json
import os
import re
from typing import Callable, Dict, Any, List, Tuple
from typing import Dict, Any, Optional

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


MONTHS = {
    "enero": "01",    "febrero": "02",    "marzo": "03",    "abril": "04",    "mayo": "05",    "junio": "06",    "julio": "07",
    "agosto": "08",    "septiembre": "09",    "setiembre": "09",
    "octubre": "10",    "noviembre": "11",    "diciembre": "12"
}

def _clean(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(r"(\w)-\s*\n(\w)", r"\1\2", text)  # palabras cortadas
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def _iso(day, month_name, year, hh, mm):
    month = MONTHS.get(month_name.lower())
    if not month:
        return None

    return f"{year}-{month}-{day.zfill(2)}T{hh.zfill(2)}:{mm}"

def extract_plazo_from_article_text(article_text):

    t = _clean(article_text)

    header = re.search(
        r"\bart[ií]culo\s+(\d+)\.\s*([^.]{1,200})\.",
        t,
        flags=re.IGNORECASE
    )

    article_number = header.group(1) if header else None
    article_title = header.group(2).strip() if header else None

    # --- CASO 1: desde ... hasta ...
    pattern_range = (
        r"\bdesde\b.*?"
        r"(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})"
        r".{0,80}?\ba\s+las\s+(\d{1,2})[,:](\d{2})"
        r".{0,200}?\bhasta\b.*?"
        r"(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})"
        r".{0,80}?\ba\s+las\s+(\d{1,2})[,:](\d{2})"
    )

    match = re.search(pattern_range, t, flags=re.IGNORECASE)

    if match:
        start_dt = _iso(match.group(1), match.group(2), match.group(3),
                        match.group(4), match.group(5))

        end_dt = _iso(match.group(6), match.group(7), match.group(8),
                      match.group(9), match.group(10))

        return {
            "article_number": article_number,
            "article_title": article_title,
            "deadline": {
                "type": "absolute",
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "timezone_note": "hora peninsular" if re.search(r"hora\s+peninsular", t, re.IGNORECASE) else None,
                "inclusive": bool(re.search(r"ambos\s+inclusive", t, re.IGNORECASE)),
                "evidence": match.group(0)
            }
        }

    # --- CASO 2  hasta el <fecha>
    pattern_until = (
        r"\bhasta\b.*?"
        r"(\d{1,2})\s+de\s+"
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"
        r"\s+de\s+(\d{4})"
    )

    matches = re.findall(pattern_until, t, flags=re.IGNORECASE)

    if matches:
        deadlines = []
        for d, m, y in matches:
            deadlines.append(_iso(d, m, y, "00", "00"))  # sin hora → 00:00

        return {
            "article_number": article_number,
            "article_title": article_title,
            "deadline": {
                "type": "until_multiple" if len(deadlines) > 1 else "until",
                "start_datetime": None,
                "end_datetime": deadlines if len(deadlines) > 1 else deadlines[0],
                "timezone_note": None,
                "inclusive": bool(re.search(r"inclusive", t, re.IGNORECASE)),
                "evidence": "hasta ..."
            }
        }

    return {
        "article_number": article_number,
        "article_title": article_title,
        "deadline": {
            "type": "unknown",
            "start_datetime": None,
            "end_datetime": None
        }
    }


def extract_plazos(pdf):

    if not isinstance(pdf, dict):
        return {"deadline": {"type": "unknown"}}

    for chapter_id, chapter_data in pdf.items():

        articles = chapter_data.get("articles", {})

        for article_id, article in articles.items():

            title = _clean(article.get("title") or "").lower()
            content = article.get("content") or ""

            if "plazo" in title:

                result = extract_plazo_from_article_text(content)

                if result.get("article_number") is None:
                    result["article_number"] = str(article_id)

                if result.get("article_title") is None:
                    result["article_title"] = article.get("title")

                result["chapter"] = chapter_id

                return result

    return {
        "article_number": None,
        "article_title": None,
        "deadline": {
            "type": "unknown",
            "start_datetime": None,
            "end_datetime": None
        }
    }



def main():
    for filename in CORPUS:
        pdf = preprocess_pdf(filename)
        print(pdf["IV"]["articles"].keys())


        info = extraction_pipeline(
            ("umbrales", pdf["IV"]["articles"]["19"]["content"], extract_umbrales),
            ("plazos", pdf, extract_plazos),

        )

        os.makedirs('information_extraction/results', exist_ok=True)
        with open(f'information_extraction/results/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

main()
