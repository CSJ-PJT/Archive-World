#!/usr/bin/env python3
"""Validate and compile Building Genomes into module placement plans only."""
import argparse,copy,hashlib,json
from pathlib import Path
REQUIRED=('footprint','massing','facade','entrance','podium','roof','ground','materials','lod')
ALIASES={'recessed-window':'recessed-bay','projected-window':'projected-bay','side-wall':'rear-service-facade','curtain-wall':'curtain-wall-panel','brick-bay':'recessed-bay','stone-panel':'spandrel','service-bay':'blind-service-bay','mechanical-band':'mechanical-floor-band','horizontal-band':'horizontal-band','blind-service-bay':'blind-service-bay','corner-bay':'corner-bay','recessed-balcony':'balcony-slab'}
MATERIALS={'painted-concrete','residential-glass','light-stone','brick','curtain-wall-glass','entrance-glazing','precast-concrete','dark-metal-panel'}
def module_ids(source):return [ALIASES.get(x,x) for x in source.get('facade',{}).get('bays',[])]
def validate(source,catalog):
 errors=[];missing=[x for x in REQUIRED if x not in source]
 if missing:errors.append({'code':'REQUIRED_GENOME_MISSING','detail':missing});return errors
 cat=source.get('category');dims=source['footprint'].get('meters',[]);floors=source['massing'].get('floors',0)
 if not source.get('entrance') or not source['entrance'].get('module'):errors.append({'code':'ENTRANCE_MISSING'})
 if not (source.get('serviceRear') if cat=='office' else source.get('parkingRamp')):errors.append({'code':'SERVICE_ACCESS_MISSING'})
 if not source.get('roof') or not source['roof'].get('module'):errors.append({'code':'ROOF_EMPTY'})
 if source.get('sideRearComplete',True) is not True:errors.append({'code':'SIDE_REAR_FACADE_MISSING'})
 if source.get('groundZ',0)!=0:errors.append({'code':'GROUND_CONTACT_FAILED'})
 if source.get('facadeRepeatRatio',.35)>.5:errors.append({'code':'FACADE_REPETITION_EXCEEDED'})
 if source.get('moduleCollisions',0)>0:errors.append({'code':'MODULE_COLLISION'})
 if len(dims)!=2 or any(x<=0 or x>120 for x in dims) or not isinstance(floors,int) or floors<2 or floors>80:errors.append({'code':'DIMENSION_OUT_OF_RANGE'})
 district=source.get('district','residential' if cat=='residential' else 'archiveos')
 ids=module_ids(source)
 missing_modules=[x for x in ids if x not in catalog]
 if missing_modules:errors.append({'code':'MODULE_UNKNOWN','detail':missing_modules})
 incompatible=[x for x in ids if x in catalog and district not in catalog[x]['districtCompatibility'] and 'all' not in catalog[x]['districtCompatibility']]
 if incompatible:errors.append({'code':'DISTRICT_MODULE_INCOMPATIBLE','detail':incompatible})
 bad_materials=[x for x in source['materials'] if x not in MATERIALS]
 if bad_materials:errors.append({'code':'MATERIAL_SLOT_INVALID','detail':bad_materials})
 lod=source['lod']
 if not(lod.get('lod0',0)>lod.get('lod1',0)>lod.get('lod2',0)>0):errors.append({'code':'LOD_INVALID'})
 return errors
def compile_genome(source,catalog):
 errors=validate(source,catalog)
 if errors:raise ValueError(json.dumps(errors))
 ids=module_ids(source);dims=source['footprint']['meters'];floors=source['massing']['floors'];digest=hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assignments=[{'moduleId':m,'facade':('front','side','rear')[i%3],'gridStart':[i%4,0],'repeatEveryFloors':max(2,(i%5)+2)} for i,m in enumerate(ids)]
 return {'id':source['id'],'category':source['category'],'district':source.get('district','residential' if source['category']=='residential' else 'archiveos'),'seed':source['seed'],'sourceHash':digest,'footprint':{'meters':dims,'groundZ':0},'massing':source['massing'],'facadeGrid':{'floors':floors,'baysPerFloor':max(4,round(dims[0]/3.2)),'repeatRatio':source.get('facadeRepeatRatio',.35)},'facadeModuleAssignments':assignments,'entrancePlan':{'module':source['entrance']['module'],'orientation':'front--Y'},'servicePlan':{'orientation':'rear+Y','present':True},'podiumPlan':source['podium'],'roofEquipmentPlan':{'module':source['roof']['module'],'mechanicalFloor':source.get('mechanicalFloor',True)},'groundInterfacePlan':{'module':source['ground']['module'],'groundZ':0},'materialAssignment':source['materials'],'lodExpectations':source['lod'],'metrics':{'footprintAreaM2':dims[0]*dims[1],'floorAreaProxyM2':dims[0]*dims[1]*floors,'moduleCount':len(ids),'uniqueFacadePatterns':len(set(ids))},'validationRules':['entrance','service','roof','side-rear','ground','repetition','collision','dimensions','district','material'],'provenance':{'mode':'GENOME_PLAN_ONLY','referenceMeshCopied':False,'canonicalStatus':'NOT_REGISTERED'},'validation':{'errors':[],'pass':True}}
def mutate(value,path,new_value):
 target=value;parts=path.split('.')
 for key in parts[:-1]:target=target[key]
 target[parts[-1]]=new_value
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path);p.add_argument('--negative-input',required=True,type=Path);p.add_argument('--module-report',required=True,type=Path);p.add_argument('--output-root',required=True,type=Path);a=p.parse_args();fixtures=json.loads(a.input.read_text());module_report=json.loads(a.module_report.read_text());catalog={x['id']:x for x in module_report['modules']};plans=[]
 for fixture in fixtures:plans.append(compile_genome(fixture,catalog))
 by_id={x['id']:x for x in fixtures};negative_results=[]
 for case in json.loads(a.negative_input.read_text()):
  candidate=copy.deepcopy(by_id[case['base']]);candidate['id']=case['id'];mutate(candidate,case['path'],case['value']);errors=validate(candidate,catalog);codes=[x['code'] for x in errors];negative_results.append({'id':case['id'],'expected':case['expectError'],'errors':codes,'pass':case['expectError'] in codes})
 result={'compiled':len(plans),'positivePass':len(plans),'negativeFixtures':len(negative_results),'negativeExpectedPass':sum(x['pass'] for x in negative_results),'failures':[]};a.output_root.mkdir(parents=True,exist_ok=True);(a.output_root/'building-genome-plans.json').write_text(json.dumps(plans,indent=2)+'\n');(a.output_root/'building-genome-negative-report.json').write_text(json.dumps(negative_results,indent=2)+'\n');(a.output_root/'building-genome-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if result['positivePass']==6 and result['negativeExpectedPass']==len(negative_results) else 1)
if __name__=='__main__':main()
