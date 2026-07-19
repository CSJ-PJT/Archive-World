from pathlib import Path
t=(Path(__file__).parents[1]/'scripts/core_district/validate_core_outputs.py').read_text()
for contract in ('actualFamilies>=12','instances>=180','proxyRatio<10%','validatorError0','graphsConnected','canonicalFalse'):assert contract in t
print('Core output validator source PASS')
