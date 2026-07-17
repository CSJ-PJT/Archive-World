"""Structural validation only. This is deliberately not a visual-quality approval."""
import argparse,json,struct
from pathlib import Path
def valid_glb(path):
 h=path.read_bytes()[:12]
 return len(h)==12 and h[:4]==b'glTF' and struct.unpack('<I',h[4:8])[0]==2 and struct.unpack('<I',h[8:12])[0]==path.stat().st_size
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);a=p.parse_args();r=Path(a.output_root);glbs=list(r.rglob('*.glb'));bad=[str(x) for x in glbs if not valid_glb(x)];meta=list(r.rglob('metadata.json'));report=json.loads((r/'report.json').read_text())
 result={'structuralPass':not bad and len(glbs)==90 and len(meta)==90,'officialKhronosValidator':'NOT_EXECUTED','reason':'Khronos CLI is not available in the current reproducible toolchain; header validation is not equivalent.','glbCount':len(glbs),'metadataCount':len(meta),'invalidGlb':bad,'generatedStatus':report['status'],'visualQuality':'NOT_APPROVED'}
 out=r/'validation';out.mkdir(exist_ok=True);(out/'structural-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 raise SystemExit(0 if result['structuralPass'] else 1)
if __name__=='__main__':main()
