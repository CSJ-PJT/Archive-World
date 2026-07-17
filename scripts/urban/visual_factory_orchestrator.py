"""Checkpointed long-run command runner; polling never restarts a running job."""
import argparse,json,os,subprocess,sys,time,uuid
from pathlib import Path
def atomic(path,data):
 t=path.with_suffix(path.suffix+'.tmp');t.write_text(json.dumps(data,indent=2));os.replace(t,path)
def load(p):return json.loads(p.read_text()) if p.exists() else {'runId':str(uuid.uuid4()),'tracks':{}}
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',required=True);p.add_argument('--track',required=True);p.add_argument('--command',nargs=argparse.REMAINDER);p.add_argument('--poll',action='store_true');a=p.parse_args();state=Path(a.state);state.parent.mkdir(parents=True,exist_ok=True);d=load(state);t=d['tracks'].get(a.track,{})
 if a.poll:
  pid=t.get('pid');alive=bool(pid and Path('/proc',str(pid)).exists());t.update({'polledAt':time.time(),'pidAlive':alive,'state':'RUNNING' if alive else t.get('state','PENDING')});d['tracks'][a.track]=t;atomic(state,d);print(json.dumps(t));return
 if t.get('state')=='PASS':print('SKIPPED completed');return
 if not a.command:raise SystemExit('command required')
 log=state.parent/(a.track+'.log');f=open(log,'ab');proc=subprocess.Popen(a.command,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);t={'state':'RUNNING','pid':proc.pid,'startedAt':time.time(),'command':a.command,'log':str(log),'attempt':t.get('attempt',0)+1};d['tracks'][a.track]=t;atomic(state,d);print(json.dumps(t))
if __name__=='__main__':main()
