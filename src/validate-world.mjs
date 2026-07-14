import { readFile } from 'node:fs/promises';
const layout = JSON.parse(await readFile(new URL('../assets/world/archive-city-v1-layout.json', import.meta.url), 'utf8'));
const ids = layout.instances.map((item) => item.instanceId); const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
const nodes = new Set(layout.roadGraph.nodes.map((node) => node.id)); const disconnectedEdges = layout.roadGraph.edges.filter(([a, b]) => !nodes.has(a) || !nodes.has(b));
const districts = new Set(layout.instances.map((item) => item.district)); const required = ['archiveos','market','nexus','logistics','ledger']; const missingDistricts = required.filter((district) => !districts.has(district));
if (duplicateIds.length || disconnectedEdges.length || missingDistricts.length || !layout.cameraPresets?.length) throw new Error(JSON.stringify({ duplicateIds, disconnectedEdges, missingDistricts, cameraPresets: layout.cameraPresets?.length ?? 0 }));
console.log(JSON.stringify({ layout: 'PASS', instances: ids.length, roadNodes: nodes.size, roadEdges: layout.roadGraph.edges.length, cameraPresets: layout.cameraPresets.length }));
