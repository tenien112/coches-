import re, os, json, requests
H={"User-Agent":"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36","Accept-Language":"es-ES,es;q=0.9"}
URLS=[
 "https://www.flexicar.es/renault/segunda-mano/",
 "https://www.flexicar.es/renault/segunda-mano/?page=2",
 "https://www.flexicar.es/combustible-diesel/renault/segunda-mano/",
 "https://www.flexicar.es/renault/megane/segunda-mano/",
 "https://www.autohero.com/es/search/?brand0=renault&page=2",
 "https://www.kia.com/es/quiero-un-kia/oferta-comercial/",
]
os.makedirs("sonda",exist_ok=True)
out=[]
for i,u in enumerate(URLS):
    try:
        r=requests.get(u,headers=H,timeout=40); t=r.text
        open(f"sonda/b{i}.html","w").write(t)
        out.append({"url":u,"status":r.status_code,"final":r.url,"len":len(t),"title":(re.search(r"<title>(.*?)</title>",t,re.S) or [None,""])[1][:120]})
    except Exception as e: out.append({"url":u,"error":str(e)})
try:
    t=open("sonda/b0.html").read()
    for c in set(re.findall(r'/_next/static/chunks/[^"]+\.js',t)):
        j=requests.get("https://www.flexicar.es"+c,headers=H,timeout=40).text
        for m in set(re.findall(r'["`](https?://[^"`]*(?:api|search|vehicle)[^"`]*)["`]',j)): out.append({"js":c,"api":m})
        for m in set(re.findall(r'["`](/api/[^"`]*)["`]',j)): out.append({"js":c,"api":m})
except Exception as e: out.append({"jserr":str(e)})
json.dump(out,open("sonda/resumen2.json","w"),indent=1,ensure_ascii=False)
