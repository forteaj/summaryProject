import re

"""
Flags:
    re.I - Case insensitive
    re.M - Multiline; matches each line instead of the whole string (whole text)
    re.S - Makes the '.' operator match new line characters as well
"""

CLEAN_PATTERNS = [
    re.compile(     # Pattern found in 25-26
        r'^.+CET\s*\n\s*Puede\s+comprobar.*?https://\S+',
        re.I | re.M
    ),
    re.compile(     # Pattern found from 21-22 to 24-25
        r'^(?:Código\s+seguro\s+de\s+Verificación|CSV)\s*:.*?\n\s*FIRMANTE.*',
        re.I | re.M | re.S
    ),
    re.compile(     # Remove page numbers
        r'(?:^\s*\n)*^\s*\d+\s*$((?:\n\s*)*)',
        re.M
    )
]

STRUCTURE_PATTERNS = {
    "chapter": re.compile(
        r'CAPÍTULO\s+([IVXLCDM]+)\s*\n(.*)',
        re.M
    ),
    "article": re.compile(
        r'Artículo\s+(\d+)[\.]?\s+(.*?)(?=Artículo\s+\d+|CAPÍTULO|\Z)',
        re.S | re.M
    )
}