"""Create deterministic PNG PBR atlas files outside Blender, then atomically publish."""
import argparse,hashlib,json,os,struct,tempfile,zlib
from pathlib import Path
MATS={'concrete':((122,122,115),(199,199,199),(128,128,255)),'glass':((33,71,97),(46,46,46),(128,128,255)),'panel':((87,99,110),(82,82,82),(128,128,255)),'stone':((107,97,82),(158,158,158),(128,128,255)),'metal':((46,54,59),(72,72,72),(128,128,255)),'white':((179,176,163),(140,140,140),(128,128,255))}
def png(w,h,rgb):
 raw=b''.join(b'\0'+bytes(rgb)*w for _ in range(h));chunk=lambda t,d:struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True);p.add_argument('--size',type=int,choices=(128,512,1024),required=True);a=p.parse_args();out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);records=[]
 for name,channels in MATS.items():
  for suffix,color in zip(('base','rough','normal'),channels):
   target=out/f'{name}-{suffix}.png';fd,tmp=tempfile.mkstemp(prefix=target.name+'.',suffix='.tmp',dir=out);os.close(fd);Path(tmp).write_bytes(png(a.size,a.size,color));data=Path(tmp).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and len(data)>64;os.replace(tmp,target);records.append({'file':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'decode':'png-signature-pass'})
 (out/'atlas-manifest.json').write_text(json.dumps({'size':a.size,'files':records,'writePolicy':'external generator; atomic rename; Blender read-only'},indent=2))
 print(json.dumps({'pass':True,'atlasDir':str(out),'files':len(records),'size':a.size},indent=2))
if __name__=='__main__':main()
