import re, os, requests
H={"User-Agent":"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36","Accept-Language":"es-ES,es;q=0.9"}
os.makedirs("sonda/js",exist_ok=True)
t=requests.get("https://www.flexicar.es/renault/megane/segunda-mano/",headers=H,timeout=40).text
for c in set(re.findall(r'/_next/static/chunks/[^"]+\.js',t)):
    open("sonda/js/"+c.split("/")[-1],"w").write(requests.get("https://www.flexicar.es"+c,headers=H,timeout=40).text)
a=requests.get("https://www.autohero.com/es/search/?brand0=renault",headers=H,timeout=40).text
for c in set(re.findall(r'src="([^"]+\.js)"',a))[:40]:
    u=c if c.startswith("http") else "https://www.autohero.com"+c
    try: open("sonda/js/ah_"+u.split("/")[-1][:80],"w").write(requests.get(u,headers=H,timeout=40).text)
    except Exception: pass
