Regex_Pattern = r'^\d{1,2}[A-Za-z]{3,}\.{0,3}$'	

import re

print(str(bool(re.search(Regex_Pattern, input()))).lower())
