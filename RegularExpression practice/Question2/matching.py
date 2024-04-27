Regex_Pattern = r'^(Mr\.|Mrs\.|Dr\.|Er\.)[A-Za-z]+$'	
import re

print(str(bool(re.search(Regex_Pattern, input()))).lower())
