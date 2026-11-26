import requests, re, os, json, sys
UA={"User-Agent":"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36","Accept-Language":"es-ES,es;q=0.9","Accept":"text/html,application/json;q=0.9,*/*;q=0.8"}
URLS=[
 "https://www.flexicar.es/",
 "https://www.flexicar.es/renault/megane/",
 "https://www.flexicar.es/coches-segunda-mano/",
 "https://www.autohero.com/es/search/?brand=renault",
 "https://www.autohero.com/es/renault/megane/",
 "https://www.renault.es/coches-ocasion.html",
 "https://www.kia.com/es/ofertas/",
 "https://www.kia.com/es/ofertas.html",
]
os.makedirs("sonda",exist_ok=True)
out=[]
for i,u in enumerate(URLS):
    try:
        r=requests.get(u,headers=UA,timeout=30)
        t=r.text
        open(f"sonda/{i}.html","w").write(t[:2000000])
        apis=sorted(set(re.findall(r'https?://[a-zA-Z0-9.\-]+/[^"\'\s<>]*(?:api|graphql|search|json)[^"\'\s<>]*',t)))[:40]
        out.append({"url":u,"status":r.status_code,"final":r.url,"len":len(t),"next_data":"__NEXT_DATA__" in t,"nuxt":"__NUXT__" in t,"apis":apis,"title":(re.search(r"<title>(.*?)</title>",t,re.S) or [None,""])[1][:120]})
    except Exception as e:
        out.append({"url":u,"error":str(e)})
json.dump(out,open("sonda/resumen.json","w"),indent=1,ensure_ascii=False)
