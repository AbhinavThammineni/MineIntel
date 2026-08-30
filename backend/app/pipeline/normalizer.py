import re
from typing import Tuple, Optional, Dict, Any, List

# Master Aliases Dictionary
SUBSIDIARY_ALIASES = {
    "bccl": "BCCL",
    "bharat coking coal": "BCCL",
    "bharat coking coal limited": "BCCL",
    "bharat coking coal ltd": "BCCL",
    "bharat coking coal ltd.": "BCCL",
    
    "ccl": "CCL",
    "central coalfields": "CCL",
    "central coalfields limited": "CCL",
    "central coalfields ltd": "CCL",
    
    "ecl": "ECL",
    "eastern coalfields": "ECL",
    "eastern coalfields limited": "ECL",
    "eastern coalfields ltd": "ECL",
    
    "secl": "SECL",
    "south eastern coalfields": "SECL",
    "south eastern coalfields limited": "SECL",
    "south eastern coalfields ltd": "SECL",
    
    "mcl": "MCL",
    "mahanadi coalfields": "MCL",
    "mahanadi coalfields limited": "MCL",
    "mahanadi coalfields ltd": "MCL",
    
    "wcl": "WCL",
    "western coalfields": "WCL",
    "western coalfields limited": "WCL",
    "western coalfields ltd": "WCL",
    
    "ncl": "NCL",
    "northern coalfields": "NCL",
    "northern coalfields limited": "NCL",
    "northern coalfields ltd": "NCL",
    
    "cmpdi": "CMPDI",
    "central mine planning and design institute": "CMPDI",
    "central mine planning & design institute": "CMPDI",
    
    "cil": "CIL",
    "coal india": "CIL",
    "coal india limited": "CIL",
    "coal india ltd": "CIL"
}

METRIC_ALIASES = {
    "production": "Coal Production",
    "coal production": "Coal Production",
    "raw coal production": "Coal Production",
    "output": "Coal Production",
    "coal output": "Coal Production",
    
    "overburden": "Overburden Removal",
    "overburden removal": "Overburden Removal",
    "ob removal": "Overburden Removal",
    "obr": "Overburden Removal",
    
    "dispatch": "Coal Dispatch",
    "coal dispatch": "Coal Dispatch",
    "offtake": "Coal Dispatch",
    "coal offtake": "Coal Dispatch",
    "despatch": "Coal Dispatch",
    
    "reserves": "Coal Reserves",
    "coal reserves": "Coal Reserves",
    "geological reserves": "Coal Reserves",
    
    "manpower": "Manpower",
    "workforce": "Manpower",
    "employees": "Manpower"
}

# Master Known Mines for Resolution
MASTER_MINES = [
    {"code": "MINE_MOONIDIH", "name": "Moonidih Underground Mine", "subsidiary": "BCCL", "state": "Jharkhand", "district": "Dhanbad"},
    {"code": "MINE_BLOCK2", "name": "Block II Opencast Mine", "subsidiary": "BCCL", "state": "Jharkhand", "district": "Dhanbad"},
    {"code": "MINE_KUSUNDA", "name": "Kusunda Opencast Mine", "subsidiary": "BCCL", "state": "Jharkhand", "district": "Dhanbad"},
    {"code": "MINE_KATRAS", "name": "Katras Choitodih Mine", "subsidiary": "BCCL", "state": "Jharkhand", "district": "Dhanbad"},
    {"code": "MINE_LODNA", "name": "Lodna Colliery", "subsidiary": "BCCL", "state": "Jharkhand", "district": "Dhanbad"},
    
    {"code": "MINE_RAJMAHAL", "name": "Rajmahal Opencast Project", "subsidiary": "ECL", "state": "Jharkhand", "district": "Godda"},
    {"code": "MINE_SONEPUR", "name": "Sonepur Bazari Project", "subsidiary": "ECL", "state": "West Bengal", "district": "Paschim Bardhaman"},
    {"code": "MINE_JHANJRA", "name": "Jhanjra Underground Mine", "subsidiary": "ECL", "state": "West Bengal", "district": "Paschim Bardhaman"},
    
    {"code": "MINE_PIPARWAR", "name": "Piparwar Opencast Mine", "subsidiary": "CCL", "state": "Jharkhand", "district": "Chatra"},
    {"code": "MINE_ASHOKA", "name": "Ashoka Opencast Project", "subsidiary": "CCL", "state": "Jharkhand", "district": "Chatra"},
    {"code": "MINE_AMRAPALI", "name": "Amrapali Opencast Mine", "subsidiary": "CCL", "state": "Jharkhand", "district": "Chatra"},
    
    {"code": "MINE_GEVRA", "name": "Gevra Opencast Project", "subsidiary": "SECL", "state": "Chhattisgarh", "district": "Korba"},
    {"code": "MINE_KUSMUNDA", "name": "Kusmunda Opencast Mine", "subsidiary": "SECL", "state": "Chhattisgarh", "district": "Korba"},
    {"code": "MINE_DIPKA", "name": "Dipka Opencast Project", "subsidiary": "SECL", "state": "Chhattisgarh", "district": "Korba"},
    
    {"code": "MINE_BHUBANESWARI", "name": "Bhubaneswari Opencast Mine", "subsidiary": "MCL", "state": "Odisha", "district": "Angul"},
    {"code": "MINE_LAKHANPUR", "name": "Lakhanpur Opencast Project", "subsidiary": "MCL", "state": "Odisha", "district": "Jharsuguda"},
    {"code": "MINE_TALCHER", "name": "Talcher Underground Mine", "subsidiary": "MCL", "state": "Odisha", "district": "Angul"},
    
    {"code": "MINE_JAYANT", "name": "Jayant Opencast Project", "subsidiary": "NCL", "state": "Madhya Pradesh", "district": "Singrauli"},
    {"code": "MINE_NIGAHI", "name": "Nigahi Opencast Mine", "subsidiary": "NCL", "state": "Madhya Pradesh", "district": "Singrauli"},
    
    {"code": "MINE_UMRER", "name": "Umrer Opencast Mine", "subsidiary": "WCL", "state": "Maharashtra", "district": "Nagpur"},
    {"code": "MINE_PENGANGA", "name": "Penganga Opencast Project", "subsidiary": "WCL", "state": "Maharashtra", "district": "Chandrapur"},
    {"code": "MINE_A", "name": "Mine A Project", "subsidiary": "BCCL", "state": "Jharkhand", "district": "Dhanbad"},
    {"code": "MINE_B", "name": "Mine B Project", "subsidiary": "BCCL", "state": "Jharkhand", "district": "Dhanbad"}
]

def levenshtein_similarity(s1: str, s2: str) -> float:
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    
    len1, len2 = len(s1), len(s2)
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j
        
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # deletion
                matrix[i][j-1] + 1,      # insertion
                matrix[i-1][j-1] + cost  # substitution
            )
    dist = matrix[len1][len2]
    max_len = max(len1, len2)
    return 1.0 - (dist / max_len)

class Normalizer:
    @staticmethod
    def normalize_unit(metric: str, raw_value: float, raw_unit: str) -> Tuple[float, str]:
        unit_clean = raw_unit.lower().replace(" ", "").replace(".", "")
        val = float(raw_value)
        
        # Coal Production / Dispatch / Reserves -> Standard MT (Million Tonnes)
        if metric in ["Coal Production", "Coal Dispatch", "Coal Reserves"]:
            if unit_clean in ["mt", "milliontonnes", "milliontonne", "mtonnes", "mtonne"]:
                return round(val, 3), "MT"
            elif unit_clean in ["kt", "kilotonnes", "kilotonne", "ktonnes", "ktonne", "thousandtonnes"]:
                return round(val * 0.001, 3), "MT"
            elif unit_clean in ["tonnes", "tonne", "tons", "ton", "t"]:
                return round(val * 0.000001, 3), "MT"
            elif unit_clean in ["lakhtonnes", "lt"]:
                return round(val * 0.1, 3), "MT"
            else:
                return round(val, 3), "MT"
                
        # Overburden Removal -> Standard MCuM (Million Cubic Metres)
        elif metric == "Overburden Removal":
            if unit_clean in ["mcum", "millioncum", "millioncubicmetres", "millionm3"]:
                return round(val, 3), "MCuM"
            elif unit_clean in ["lcm", "lakhcum", "lakhcubicmetres"]:
                return round(val * 0.1, 3), "MCuM"
            elif unit_clean in ["cum", "m3", "cubicmetres"]:
                return round(val * 0.000001, 3), "MCuM"
            else:
                return round(val, 3), "MCuM"
                
        # Manpower -> Integer count
        elif metric == "Manpower":
            return round(val), "Persons"
            
        return round(val, 3), raw_unit

    @staticmethod
    def normalize_subsidiary(raw_name: str) -> str:
        clean = raw_name.lower().strip().replace(".", "").replace(",", "")
        return SUBSIDIARY_ALIASES.get(clean, raw_name.upper())

    @staticmethod
    def normalize_metric(raw_metric: str) -> str:
        clean = raw_metric.lower().strip()
        return METRIC_ALIASES.get(clean, raw_metric.title())

    @staticmethod
    def normalize_fiscal_year(raw_year: str) -> str:
        raw_year = str(raw_year).strip()
        # e.g., "2023-2024" or "2023-24" or "FY 2023-24" or "2023"
        match_fy = re.search(r'(\d{4})[-/](\d{2,4})', raw_year)
        if match_fy:
            start = match_fy.group(1)
            end = match_fy.group(2)
            if len(end) == 4:
                end = end[2:]
            return f"{start}-{end}"
        
        match_single = re.search(r'\b(19\d{2}|20\d{2})\b', raw_year)
        if match_single:
            y = int(match_single.group(1))
            next_y = (y + 1) % 100
            return f"{y}-{next_y:02d}"
            
        return raw_year

    @staticmethod
    def resolve_mine_entity(raw_mine_name: str, preferred_subsidiary: Optional[str] = None) -> Dict[str, Any]:
        raw_clean = raw_mine_name.lower().strip()
        best_match = None
        best_score = 0.0
        
        for mine in MASTER_MINES:
            # Check exact code or name match
            if mine["code"].lower() == raw_clean or mine["name"].lower() == raw_clean:
                return mine
                
            # Direct name contains
            if raw_clean in mine["name"].lower() or mine["name"].lower() in raw_clean:
                score = 0.90
            else:
                score = levenshtein_similarity(raw_clean, mine["name"])
                
            # Boost if subsidiary matches
            if preferred_subsidiary and mine["subsidiary"].upper() == preferred_subsidiary.upper():
                score += 0.08
                
            if score > best_score:
                best_score = score
                best_match = mine
                
        if best_match and best_score >= 0.65:
            return best_match
            
        # Fallback if unknown mine
        return {
            "code": f"MINE_{re.sub(r'[^a-zA-Z0-9]', '_', raw_mine_name.upper())[:12]}",
            "name": raw_mine_name.title(),
            "subsidiary": preferred_subsidiary or "BCCL",
            "state": "Unknown",
            "district": "Unknown"
        }