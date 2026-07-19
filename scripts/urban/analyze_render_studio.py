#!/usr/bin/env python3
"""Dependency-free PNG luminance checks for Render Studio outputs."""
import argparse,json,math,statistics,struct,zlib
from pathlib import Path
SIG=b'\x89PNG\r\n\x1a\n'
def decode(path):
 data=path.read_bytes();assert data[:8]==SIG;pos=8;raw=b'';w=h=ctype=None
 while pos<len(data):
  n=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];chunk=data[pos+8:pos+8+n];pos+=12+n
  if kind==b'IHDR':w,h,depth,ctype,_,_,_=struct.unpack('>IIBBBBB',chunk);assert depth==8 and ctype in (2,6)
  elif kind==b'IDAT':raw+=chunk
  elif kind==b'IEND':break
 channels=4 if ctype==6 else 3;scan=zlib.decompress(raw);stride=w*channels;rows=[];i=0;prior=bytearray(stride)
 for _ in range(h):
  f=scan[i];i+=1;row=bytearray(scan[i:i+stride]);i+=stride
  for x in range(stride):
   a=row[x-channels] if x>=channels else 0;b=prior[x];c=prior[x-channels] if x>=channels else 0
   if f==1:row[x]=(row[x]+a)&255
   elif f==2:row[x]=(row[x]+b)&255
   elif f==3:row[x]=(row[x]+((a+b)//2))&255
   elif f==4:
    p=a+b-c;pa=abs(p-a);pb=abs(p-b);pc=abs(p-c);row[x]=(row[x]+(a if pa<=pb and pa<=pc else b if pb<=pc else c))&255
  rows.append(row);prior=row
 lum=[]
 for row in rows:
  for x in range(0,len(row),channels):lum.append((.2126*row[x]+.7152*row[x+1]+.0722*row[x+2])/255)
 return w,h,lum
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);a=p.parse_args();raw=json.loads((a.root/'render-studio-raw-report.json').read_text());out=[]
 for item in raw['reports']:
  w,h,lum=decode(a.root/item['output']);ordered=sorted(lum);q=lambda v:ordered[int((len(ordered)-1)*v)];mean=statistics.fmean(lum);var=statistics.pvariance(lum);expected=item['expectedLuminance'];metrics={'width':w,'height':h,'mean':mean,'p05':q(.05),'p50':q(.5),'p95':q(.95),'blackClipping':sum(v<.01 for v in lum)/len(lum),'whiteClipping':sum(v>.99 for v in lum)/len(lum),'blankFrame':var<.0005,'modelOccupancyProxy':sum(abs(v-mean)>.08 for v in lum)/len(lum),'contrast':math.sqrt(var)};item.update(metrics);item['pass']=not item['blankFrame'] and item['bytes']>1024 and item['pngSignature']==SIG.hex() and expected[0]<=mean<=expected[1];out.append(item)
 result={'presets':raw['presets'],'targets':raw['targets'],'passed':sum(x['pass'] for x in out),'reports':out,'externalAnalyzer':'stdlib-png','absoluteUserPaths':0};(a.root/'render-studio-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'presets':result['presets'],'passed':result['passed']}));raise SystemExit(0 if result['passed']==result['presets'] else 1)
if __name__=='__main__':main()
