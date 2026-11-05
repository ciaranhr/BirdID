import json,urllib.request,sys,time
S=sys.argv[1]
sp=json.load(open(S+'/inat_species.json'))
ids=[s['taxon']['id'] for s in sp]; res={}
for i in range(0,len(ids),30):
    u="https://api.inaturalist.org/v1/taxa/"+",".join(map(str,ids[i:i+30]))+"?locale=en-AU"
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'BirdID-personal-app'})))
    for t in d['results']:
        a={x['rank']:(x['name'],x.get('preferred_common_name')) for x in t.get('ancestors',[])}
        res[t['id']]={'family':a.get('family'),'order':a.get('order'),'genus':a.get('genus'),'syn':[n['name'] for n in t.get('names',[]) if n.get('locale')=='sci'] if t.get('names') else []}
    time.sleep(1.2)
json.dump(res,open(S+'/inat_anc.json','w')); print(len(res))
