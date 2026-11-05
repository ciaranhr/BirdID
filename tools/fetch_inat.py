import json,urllib.request,sys,time
S=sys.argv[1]; out=[]; page=1
while True:
    u=f"https://api.inaturalist.org/v1/observations/species_counts?taxon_id=3&place_id=6744&quality_grade=research&per_page=500&page={page}&locale=en-AU"
    req=urllib.request.Request(u,headers={'User-Agent':'BirdID-personal-app'})
    d=json.load(urllib.request.urlopen(req))
    out+=d['results']; print(page,d['total_results'],len(out))
    if len(out)>=d['total_results'] or not d['results']: break
    page+=1; time.sleep(1.5)
json.dump(out,open(S+'/inat_species.json','w'))
