from pathlib import Path
t=(Path(__file__).parents[1]/'scripts/blender/core_district_precision/infrastructure_generator.py').read_text()
for required in ('raised-sidewalk','curb','crosswalk','transit-shelter','archive-plaza','ledger-plaza','station-entrance','tree-trunk','tree-crown-lobe','vehicle-body','vehicle-wheel','human-torso','human-head','lane-marking-dash','block-parcel-surface','block-courtyard-groundcover','parcelFields','midDetailPopulation'):
 assert required in t,required
assert "'roadSegments':10" in t and "'stationEntrances':2" in t
print('Core district infrastructure source PASS')
