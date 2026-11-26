import os, requests
H={"User-Agent":"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36","Accept-Language":"es-ES,es;q=0.9"}
os.makedirs("sonda",exist_ok=True)
for k,u in {"renew1":"https://es.renew.auto/vehiculos.html?brand.label.raw=RENAULT&model.label.raw=MEGANE&energy.groupLabel.raw=di%C3%A9sel",
            "renew2":"https://es.renew.auto/vehiculos.html?brand.label.raw=RENAULT&model.label.raw=MEGANE&energy.groupLabel.raw=di%C3%A9sel&page=2"}.items():
    r=requests.get(u,headers=H,timeout=40); open(f"sonda/{k}.txt","w").write(f"{r.status_code} {r.url}\n"+r.text)
