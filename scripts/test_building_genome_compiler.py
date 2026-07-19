#!/usr/bin/env python3
import json,sys
from pathlib import Path
positive=json.loads(Path('config/building-genome-fixtures.json').read_text());negative=json.loads(Path('config/building-genome-negative-fixtures.json').read_text());assert len(positive)==6 and len(negative)>=6;assert len({x['id'] for x in positive})==6;assert len({x['expectError'] for x in negative})>=6
source=Path('scripts/urban/building_genome_compiler.py').read_text();assert 'GENOME_PLAN_ONLY' in source and 'canonicalStatus' in source and 'C:/Users/' not in source
if len(sys.argv)>1:
 report=json.loads(Path(sys.argv[1]).read_text());assert report['compiled']==6 and report['positivePass']==6 and report['negativeExpectedPass']==report['negativeFixtures']
print('building genome compiler contracts PASS')
