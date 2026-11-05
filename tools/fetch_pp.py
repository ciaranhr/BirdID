import json,urllib.request,sys,time
S=sys.argv[1]
A='667b8664-5dd7-487e-ba56-c6c5c95055a2'
out=[]
for p in range(34):
    u=f"https://api.phylopic.org/images?build=562&filter_clade={A}&page={p}&embed_items=true&embed_specificNode=true&embed_contributor=true"
    d=json.load(urllib.request.urlopen(u))
    out+=d['_embedded']['items']
json.dump(out,open(S+'/pp/all.json','w'))
print(len(out))
