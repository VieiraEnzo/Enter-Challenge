import re
from typing import Optional, Any

# Dictionary of compiled regex patterns for common fields
REGEX_LIBRARY = {
    
    # Código de Estado/Seccional (ex: "PR", "GO" )
    "STATE_CODE": re.compile(r"(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO|BR)"),
            
    # VALOR/Moeda:  
    "VALOR": re.compile(r"^R?\$?\s?(\d{1,3}(\.\d{3})*|\d+)(,\d{2})$"),

    # Data BR (ex: "05/09/2025", "04/02/2021")
    "DATA_BR": re.compile(r"(0[1-9]|1[0-9]|2[0-9]|3[0-1])[- | \/](0[1-9]|1[0-2])[- | \/]([0-9]{4})"),
    
    # Telefone BR
    "TELEFONE_BR": re.compile(r"(?:(?:(\+|00)?(55))\s?)?(?:\(?(\d{2})\)?\s?)(|\d{2})(|-)?(?:(9\d|[2-9])\d{3}[-|.|\s]?(\d{4}))"),
    
    # Email
    "EMAIL": re.compile(r"([\w._%+-]+)(@|\s@\s|\sat\s|\[at\])([\w.-]+)\.([\w]{2,})"),
    
    # RG
    "RG": re.compile(r"(\d{1,2}\.?)(\d{3}\.?)(\d{3})(\-?[0-9Xx]{1})"),

    # CNH
    "CNH": re.compile(r"((cnh.*[0-9]{11})|(CNH.*[0-9]{11})|(habilitação.*[0-9]{11})|(carteira.*[0-9]{11}))"),

    #HORA (12hrs)
    "HORA12" : re.compile(r"((0?[1-9]|1[0-2]):([0-5][0-9].?([a].?[m].?|[p].?[m].?)))"),

    #HORA (24hrs)
    "HORA12" : re.compile(r"([01][0-9]|[2][0-3]):([0-5][0-9])"),

    #LAT/LONG
    "LATLONG" : re.compile(r"(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))"),

    # CPF: Aceita xxx.xxx.xxx-xx OU xxxxxxxxxxx
    "CPF": re.compile(r"(^\d{3}.?\d{3}.?\d{3}\-?\d{2}$)"),

    # CNPJ: Aceita xx.xxx.xxx/xxxx-xx OU xxxxxxxxxxxxxx
    "CNPJ": re.compile(r"^(\d{2}.?\d{3}.?\d{3}\/?\d{4}\-?\d{2})$"),

    # N1: Exatamente 1 dígito
    "N1" : re.compile(r"^\d{1}$"),

    # N2: Exatamente 2 dígitos
    "N2" : re.compile(r"^\d{2}$"),

    # N3: Exatamente 3 dígitos
    "N3" : re.compile(r"^\d{3}$"),

    # N4: Exatamente 4 dígitos
    "N4" : re.compile(r"^\d{4}$"),

    # N5: Exatamente 5 dígitos
    "N5" : re.compile(r"^\d{5}$"),

    # N6: Exatamente 6 dígitos
    "N6" : re.compile(r"^\d{6}$"),

    # N7: Exatamente 7 dígitos
    "N7" : re.compile(r"^\d{7}$"),

    # CEP: Aceita xxxxx-xxx OU xxxxxxxx
    "CEP": re.compile(r"(^\d{5})\-?(\d{3}$)"),

    # N9: Exatamente 9 dígitos
    "N9" : re.compile(r"^\d{9}$"),

    # N10: Exatamente 10 dígitos
    "N10" : re.compile(r"^\d{10}$"),

}

def find_matching_rule(value: Any) -> Optional[str]:
    """
    Tests a value against all patterns in REGEX_LIBRARY and returns the matching rule name.
    
    Args:
        value (Any): The value to test against regex patterns. Will be converted to string.
        
    Returns:
        Optional[str]: The name of the unique matching rule, or None if no unique match is found
    """
    # Handle None values
    if value is None:
        return None
        
    # Convert value to string
    try:
        str_value = str(value).strip()
    except:
        return None
        
    matches = []
    
    # Test value against each pattern
    for rule_name, pattern in REGEX_LIBRARY.items():
        if pattern.fullmatch(str_value):
            matches.append(rule_name)
    
    # Return rule name only if there's exactly one match
    return matches[0] if len(matches) == 1 else None
