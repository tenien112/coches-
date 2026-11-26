import re, os, requests
H={"User-Agent":"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36","Accept-Language":"es-ES,es;q=0.9"}
os.makedirs("sonda",exist_ok=True)
U={"kiajs":"https://www.kia.com/etc.clientlibs/settings/wcm/designs/eutSpec/clientlib/es/components/commercial-offer.min.c87ad98f6a2f0d61de6c91628e64fbde.js",
   "kiasemi":"https://www.kia.com/es/soluciones-de-movilidad/kia-seminuevos-certificados-/",
   "renault":"https://www.renault.es/coches-ocasion.html"}
for k,u in U.items():
    try:
        r=requests.get(u,headers=H,timeout=40); open(f"sonda/{k}.txt","w").write(f"{r.status_code} {r.url}\n"+r.text)
    except Exception as e: open(f"sonda/{k}.txt","w").write("ERR "+str(e))
