import json,urllib.request,sys,time,urllib.parse
S=sys.argv[1]
anc=json.load(open(S+'/inat_anc.json'))
fams=sorted({v['family'][0] for v in anc.values() if v['family']})
H={'User-Agent':'BirdID-personal-app'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H)))
res={}
for f in fams:
    try:
        d=get(f"https://api.phylopic.org/nodes?build=562&filter_name={urllib.parse.quote(f.lower())}&page=0")
        items=d['_links'].get('items',[])
        if not items: res[f]=[]; continue
        nid=items[0]['href'].split('/')[2].split('?')[0]
        d=get(f"https://api.phylopic.org/images?build=562&filter_clade={nid}&page=0")
        res[f]=[x['href'].split('/')[2].split('?')[0] for x in d['_links'].get('items',[])]
    except Exception as e:
        res[f]=[]; print(f,e)
    time.sleep(0.3)
json.dump(res,open(S+'/pp/fam.json','w'))
print(len(fams), sum(1 for v in res.values() if v), [f for f,v in res.items() if not v])
