from invoice2data import extract_data
from invoice2data.extract.loader import read_templates

templates = read_templates('Template/')
print(templates)
result = extract_data(r'C:\Users\HomePC\Documents\PERSONAL PROJECTS\INVOICE2DATAMODEL\Invoice\QualityHosting_test.pdf', templates=templates)
print(result)