"""Dry-run Urban Grammar skeleton. It plans, but never mutates layout or runtime."""
import argparse, json
STAGES=("Building","Family","Block","Street","District","City")
def main():
 p=argparse.ArgumentParser();p.add_argument("--district",required=True);p.add_argument("--seed",type=int,default=1);a=p.parse_args()
 plan={"district":a.district,"seed":a.seed,"stages":list(STAGES),"contracts":{"maxSameAssetPerCamera":2,"generatedOutput":"external-only","layoutMutation":False,"canonicalMutation":False},"status":"PLAN_ONLY"}
 print(json.dumps(plan,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
