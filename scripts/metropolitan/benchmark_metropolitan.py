#!/usr/bin/env python3
"""CPU/manifest performance baseline; deliberately does not claim Viewer FPS."""
import json,time,tracemalloc
from .city_assembler import assemble_city

def benchmark():
 city=assemble_city(); results=[]
 for count in (500,1000,2500,len(city['instances'])):
  sample=city['instances'][:count];tracemalloc.start();start=time.perf_counter();encoded=json.dumps(sample,separators=(',',':')).encode();encode_ms=(time.perf_counter()-start)*1000
  start=time.perf_counter();decoded=json.loads(encoded);decode_ms=(time.perf_counter()-start)*1000;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
  results.append({"instances":count,"manifestBytes":len(encoded),"encodeMs":round(encode_ms,3),"decodeMs":round(decode_ms,3),"pythonPeakMiB":round(peak/1048576,3),"decoded":len(decoded)})
 return {"status":"PASS","scope":"manifest-cpu-baseline-not-viewer-fps","results":results,"viewerFps":None,"viewerGpuMemory":None,"chunkPolicy":{"district":True,"block":True,"spatialIndex":True}}

if __name__=='__main__': print(json.dumps(benchmark(),indent=2))

