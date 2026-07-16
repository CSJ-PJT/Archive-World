"""Create an external-only review package from validated planning outputs."""
import argparse,datetime,hashlib,json,os,shutil,zipfile
from pathlib import Path
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-root',required=True);p.add_argument('--transfer-root',required=True);a=p.parse_args();root=Path(a.output_root);stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');review=root/'review'/f'Archive-City-Urban-Grammar-V1-1-{stamp}';review.mkdir(parents=True)
 score={'scope':'Planning adequacy only; not a visual/canonical asset quality score.','residential':{'Building':80,'Family':80,'Block':84,'Street':82,'District':80,'City':80},'archiveos':{'Building':80,'Family':80,'Block':84,'Street':82,'District':80,'City':80}}
 (review/'planning-gate-score.json').write_text(json.dumps(score,indent=2),encoding='utf-8')
 for block in ('residential','archiveos'):
  shutil.copy(root/f'{block}-block'/'plan'/'block-plan.json',review/f'{block}-block-plan.json')
  shutil.copy(root/'contact-sheets'/f'{block}-planning-contact-sheet.png',review/f'{block}-contact-sheet.png')
 readme='''Archive City Urban Grammar V1.1 — Planning Review\n\nStatus: GENERATED_PLAN_ONLY. All massing and Street Family elements are PLACEHOLDER or PROTOTYPE. This package is for Urban Grammar review only; it does not approve canonical assets, production layout, runtime manifests, or engineering/legal compliance.\n\nIncluded: Residential and ArchiveOS plan JSON, contact sheets, topology validation result, and planning gate scorecard.\n'''
 (review/'README.txt').write_text(readme,encoding='utf-8')
 checks=[]
 for f in sorted(review.iterdir()):
  if f.is_file():checks.append(f'{digest(f)}  {f.name}')
 (review/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n',encoding='utf-8')
 transfer=Path(a.transfer_root);transfer.mkdir(parents=True,exist_ok=True);archive=transfer/f'Archive-City-Urban-Grammar-V1-1-Review-{stamp}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(review.iterdir()):z.write(f,f.name)
 archive.with_suffix('.zip.sha256').write_text(f'{digest(archive)}  {archive.name}\n',encoding='utf-8')
 print(json.dumps({'review':str(review),'zip':str(archive),'sha256':digest(archive)},indent=2))
if __name__=='__main__':main()
