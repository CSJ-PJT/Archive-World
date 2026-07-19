#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,tempfile,os
from pathlib import Path

def atomic(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.tmp')
 with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)

def plan():
 points=[[-390,-24],[-260,-12],[-130,10],[0,0],[130,-16],[260,-6],[390,18]]
 edges=['formal-stone','stepped-seating','green-planted','plaza-terrace','transit-frontage','low-retaining']
 segments=[]
 for i,(a,b) in enumerate(zip(points,points[1:])):
  length=math.dist(a,b);segments.append({'id':f'stream-segment-{i+1}','start':a,'end':b,'lengthM':round(length,2),'waterWidthM':10+i%3*2,'corridorWidthM':30+i%2*6,'depthM':.35+i%2*.12,'elevationM':round(-.05*i,2),'edgeType':edges[i]})
 bridges=[{'id':f'bridge-{i+1}','type':t,'position':[x,y],'clearanceM':2.7,'accessible':i!=5} for i,(x,y,t) in enumerate([(-310,-18,'slim-steel'),(-195,-2,'stone-plaza'),(-70,5,'green-corridor'),(65,-8,'archive-gateway'),(185,-11,'transit-connector'),(300,4,'service-crossing'),(360,13,'street-crossing')])]
 access=[{'id':f'access-{i+1}','position':[x,y],'type':'ramp' if i%3 else 'stair-ramp','accessible':True} for i,(x,y) in enumerate([(-375,-40),(-300,6),(-210,-25),(-95,27),(25,-25),(145,8),(250,-26),(375,36)])]
 nodes=[{'id':'archive-water-plaza','role':'MAJOR','position':[-240,-10]},{'id':'ledger-stream-terrace','role':'MAJOR','position':[60,-4]},{'id':'transit-stream-junction','role':'MAJOR','position':[260,-4]}]+[{'id':f'pocket-node-{i+1}','role':'POCKET','position':[x,y]} for i,(x,y) in enumerate([(-345,-22),(-125,18),(155,-20),(345,16)])]
 return {'schemaVersion':1,'name':'Archive Urban Stream','lengthM':round(sum(x['lengthM'] for x in segments),2),'centerline':points,'segments':segments,'bridges':bridges,'accessPoints':access,'nodes':nodes,'adjacentReworkedBlocks':[f'core-block-{i:02d}' for i in (7,8,9,10,11,12,13,14)],'futureConnection':'RIVERFRONT_INTERFACE_ONLY','originality':'NON_SPECIFIC_URBAN_TYPE_NO_DIRECT_COPY'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();data=plan();atomic(a.output,data);print(json.dumps({'status':'PASS','lengthM':data['lengthM'],'segments':len(data['segments']),'bridges':len(data['bridges']),'access':len(data['accessPoints']),'nodes':len(data['nodes'])}))
