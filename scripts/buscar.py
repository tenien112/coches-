"""COCHES-LORENZITO · buscador diario.
Busca en Flexicar y Autohero los coches que encajan con los criterios de Lorenzo
y deja el resultado en datos/coches.json. Avisa por ntfy si entran coches nuevos."""
import re, json, os, time, datetime, html, requests

H = {"User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36",
     "Accept-Language": "es-ES,es;q=0.9"}
PMIN, PMAX = 8000, 14000
ENTRADA = 10000
NTFY = os.environ.get("NTFY_TOPIC", "")

# (marca, modelo flexicar, modelo autohero, preferencia 1=la que más le gusta)
MODELOS = [
    ("renault", "megane", "megane", 1),
    ("renault", "kadjar", "kadjar", 2),
    ("renault", "captur", "captur", 3),
    ("kia", "ceed", "ceed", 4),
    ("kia", "sportage", "sportage", 4),
    ("kia", "niro", "niro", 5),
    ("kia", "stonic", "stonic", 5),
]

def norm_fuel(f):
    f = (f or "").lower()
    if "di" in f and "sel" in f: return "Diésel"
    if "híbrido" in f or "hibrido" in f or "hybrid" in f: return "Híbrido"
    if "gasolina" in f or "petrol" in f: return "Gasolina"
    if "eléctr" in f or "electr" in f: return "Eléctrico"
    return (f or "?").capitalize()

def motor_malo(txt):
    t = (txt or "").lower()
    return "bluehdi" in t or "puretech" in t

def get(url):
    for i in range(3):
        try:
            r = requests.get(url, headers=H, timeout=40)
            if r.status_code == 200: return r.text
            print("HTTP", r.status_code, url)
        except Exception as e:
            print("ERR", e, url)
        time.sleep(3)
    return ""

# ---------------- FLEXICAR ----------------
def flexicar(marca, modelo, pref):
    out, page = [], 1
    while page <= 15:
        url = (f"https://www.flexicar.es/coches-segunda-mano/search?brands={marca}&models={modelo}"
               f"&priceFrom={PMIN-1000}&priceTo={PMAX}" + (f"&page={page}" if page > 1 else ""))
        t = get(url)
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, re.S)
        if not m: break
        pp = json.loads(m.group(1))["props"]["pageProps"]
        vs = pp.get("initialVehicles") or []
        nuevos = 0
        for v in vs:
            vid = "fx" + str(v["id"])
            if any(c["id"] == vid for c in out): continue
            nuevos += 1
            contado = v.get("cashPrice") or v.get("price")
            fin = v.get("price")
            out.append({
                "id": vid, "web": "Flexicar", "marca": v.get("brand"), "modelo": v.get("model"),
                "version": v.get("version"), "anio": v.get("year"), "km": v.get("km"),
                "precio": contado, "precio_fin": fin if fin and fin != contado else None,
                "cuota": v.get("quotaPrice"), "combustible": norm_fuel(v.get("fuel")),
                "cambio": v.get("transmission"), "lugar": v.get("carDealership"),
                "reservado": bool(v.get("reserved")), "foto": v.get("image"),
                "url": f"https://www.flexicar.es/{v.get('slug')}/", "pref": pref})
        if not vs or nuevos == 0: break
        page += 1
        time.sleep(1.5)
    return out

# ---------------- AUTOHERO ----------------
def autohero(marca, modelo, pref):
    out, page = [], 1
    while page <= 15:
        url = f"https://www.autohero.com/es/search/?brand0={marca}&models0={modelo}" + (f"&px={page}" if page > 1 else "")
        t = get(url)
        cards = t.split('data-qa-selector="ad-card-link"')[1:]
        nuevos = 0
        for c in cards:
            idm = re.search(r'id="([0-9a-f-]{36})"', c[:600])
            if not idm: continue
            vid = "ah" + idm.group(1)
            if any(x["id"] == vid for x in out): continue
            c = re.sub(r"<svg.*?</svg>", "", c[:12000], flags=re.S)
            txt = [html.unescape(s).strip() for s in re.sub(r"<[^>]+>", "|", c).split("|")]
            txt = [s for s in txt if s and s != "•"]
            def num(s): return int(re.sub(r"[^\d]", "", s)) if re.search(r"\d", s) else None
            precios = [num(s) for s in txt if s.endswith("€") and "/mes" not in s]
            cuota = next((num(s) for s in txt if "/mes" in s), None)
            anio = next((int(s) for s in txt if re.fullmatch(r"(19|20)\d\d", s)), None)
            km = next((num(s) for s in txt if s.endswith(" km")), None)
            fuel = next((s for s in txt if s in ("Gasolina", "Diésel", "Diesel", "Híbrido", "Eléctrico", "GLP", "Híbrido enchufable")), "")
            cambio = next((s for s in txt if s in ("Manual", "Automático")), "")
            al = re.search(r'aria-label="([^"]+)"', c)
            partes = html.unescape(al.group(1)).split(" - ") if al else []
            img = re.search(r'<img src="([^"]+)"', c)
            href = re.search(r'href="(/es/[^"]+/id/[^"]+)"', t[t.find(idm.group(1)) - 400:t.find(idm.group(1)) + 50])
            fin = precios[0] if precios else None
            contado = fin
            if "Al contado" in txt:
                k = txt.index("Al contado")
                contado = next((num(s) for s in txt[k + 1:k + 4] if s.endswith("€")), fin)
            nuevos += 1
            out.append({
                "id": vid, "web": "Autohero", "marca": marca.capitalize(),
                "modelo": (partes[0].split(" ", 1)[1] if partes and " " in partes[0] else modelo.capitalize()),
                "version": partes[1] if len(partes) > 1 else "", "anio": anio, "km": km,
                "precio": contado, "precio_fin": fin if fin != contado else None, "cuota": cuota,
                "combustible": norm_fuel(fuel), "cambio": cambio, "lugar": "Entrega a domicilio",
                "reservado": False, "foto": img.group(1) if img else None,
                "url": "https://www.autohero.com" + (href.group(1) if href else f"/es/{marca}-{modelo}/id/{idm.group(1)}/"),
                "pref": pref})
        if not cards or nuevos == 0: break
        page += 1
        time.sleep(1.5)
    return out

def puntua(c):
    """Más puntos = mejor para Lorenzo."""
    p = 100 - c["pref"] * 8
    if c["combustible"] == "Diésel": p += 25
    if "dci" in (c["version"] or "").lower(): p += 10
    if c["km"]: p -= c["km"] / 10000          # -1 por cada 10.000 km
    if c["anio"]: p += (c["anio"] - 2016) * 3
    if c["precio"]: p -= max(0, c["precio"] - ENTRADA) / 1000 * 2   # financiar resta
    if c["reservado"]: p -= 30
    return round(p, 1)

def main():
    os.makedirs("datos", exist_ok=True)
    prev = {}
    try:
        prev = {c["id"]: c for c in json.load(open("datos/coches.json"))["coches"]}
    except Exception:
        pass
    todos, fallos = [], []
    for marca, mf, ma, pref in MODELOS:
        for fn, mod, web in ((flexicar, mf, "Flexicar"), (autohero, ma, "Autohero")):
            try:
                r = fn(marca, mod, pref)
                print(web, marca, mod, len(r))
                todos += r
            except Exception as e:
                print("FALLO", web, marca, mod, e); fallos.append(f"{web} {mod}")
    coches = []
    hoy = datetime.date.today().isoformat()
    for c in todos:
        if not c["precio"] or not (PMIN <= c["precio"] <= PMAX or (c["precio_fin"] and PMIN <= c["precio_fin"] <= PMAX)):
            continue
        if motor_malo(c["version"]): continue
        c["financiar"] = max(0, c["precio"] - ENTRADA)
        c["puntos"] = puntua(c)
        c["visto"] = prev.get(c["id"], {}).get("visto", hoy)
        coches.append(c)
    coches.sort(key=lambda c: -c["puntos"])
    nuevos = [c for c in coches if c["id"] not in prev]
    json.dump({"actualizado": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               "criterios": {"min": PMIN, "max": PMAX, "entrada": ENTRADA},
               "fallos": fallos, "coches": coches},
              open("datos/coches.json", "w"), ensure_ascii=False, indent=0)
    print("TOTAL", len(coches), "nuevos", len(nuevos))
    if NTFY and prev and nuevos:
        top = sorted(nuevos, key=lambda c: -c["puntos"])[:5]
        txt = "\n".join(f"{c['modelo']} {c['anio']} · {c['km']:,} km · {c['precio']:,} € ({c['web']})".replace(",", ".") for c in top)
        requests.post(f"https://ntfy.sh/{NTFY}", data=txt.encode(),
                      headers={"Title": f"COCHES-LORENZITO: {len(nuevos)} coches nuevos".encode("utf-8"),
                               "Click": "https://tenien112.github.io/coches-/", "Tags": "car"})

if __name__ == "__main__":
    main()
