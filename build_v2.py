#!/usr/bin/env python3
"""Version 2 : communes avec données ADEME, secteurs, pages service × secteur, observatoire, questionnaire, actualités."""
import sys, unicodedata, re, shutil
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B
from build_site import page, ul, cartes, faq_html, faq_ld, e, TEL, TEL_LINK, MAIL, BASE, OUT, DIAGS

NOMS = ["Lesneven","Le Folgoët","Ploudaniel","Plouider","Kerlouan","Guissény","Plounéour-Brignogan-Plages","Goulven","Kernilis","Lanarvily","Saint-Méen","Trégarantec","Kernouës","Saint-Frégant","Plabennec","Bourg-Blanc","Le Drennec","Kersaint-Plabennec","Plouvien","Lannilis","Plouguerneau","Landéda","Brest","Guipavas","Le Relecq-Kerhuon","Gouesnou","Bohars","Guilers","Plouzané","Plougastel-Daoulas","Landerneau","Plouédern","La Roche-Maurice","Saint-Thonan","Pencran","Dirinon","Landivisiau","Plouvorn","Plounéventer","Bodilis","Lampaul-Guimiliau","Saint-Pol-de-Léon","Roscoff","Plouescat","Cléder","Saint-Renan","Ploudalmézeau","Plouarzel","Milizac-Guipronvel","Plouguin","Morlaix","Saint-Martin-des-Champs","Plourin-lès-Morlaix","Carantec","Taulé","Plouénan","Le Conquet","Locmaria-Plouzané","Ploumoguer","Lampaul-Plouarzel","Saint-Pabu","Tréglonou","Coat-Méal","Plouzévédé","Sizun","Daoulas","Loperhet","Saint-Divy","La Forest-Landerneau","Saint-Urbain"]
EXCLUS = {68}  # données incohérentes dans la base pour cette commune
ZONES = [  # (slug, ville centre, libellé, « dans … », indices des communes)
 ("lesneven", "Lesneven", "Lesneven et la Côte des Légendes", "à Lesneven et sur la Côte des Légendes", list(range(0, 14))),
 ("abers", "Lannilis", "Plabennec, Lannilis et les Abers", "à Plabennec, Lannilis et dans les Abers", list(range(14, 22)) + [49, 60, 61, 62]),
 ("brest", "Brest", "Brest et sa métropole", "à Brest et dans sa métropole", list(range(22, 30))),
 ("landerneau", "Landerneau", "Landerneau et Daoulas", "à Landerneau et dans le pays de Daoulas", list(range(30, 36)) + [65, 66, 67, 69]),
 ("landivisiau", "Landivisiau", "Landivisiau et son secteur", "à Landivisiau et dans son secteur", list(range(36, 41)) + [63, 64]),
 ("haut-leon", "Saint-Pol-de-Léon", "Saint-Pol-de-Léon, Roscoff et le Haut-Léon", "à Saint-Pol-de-Léon, Roscoff et dans le Haut-Léon", [41, 42, 43, 44, 55]),
 ("iroise", "Saint-Renan", "Saint-Renan et le pays d'Iroise", "à Saint-Renan et dans le pays d'Iroise", [45, 46, 47, 48, 56, 57, 58, 59]),
 ("morlaix", "Morlaix", "Morlaix et sa baie", "à Morlaix et autour de sa baie", [50, 51, 52, 53, 54]),
]
SERVICES_ZONE = ["dpe", "audit-energetique", "pppt", "dtg"]
TITRES_ZONE = {"dpe": "DPE {centre} : diagnostic de performance énergétique | Arliane", "audit-energetique": "Audit énergétique {centre} : maisons classées E, F ou G | Arliane",
               "pppt": "PPPT {centre} : plan pluriannuel de travaux de copropriété | Arliane", "dtg": "DTG {centre} : diagnostic technique global de copropriété | Arliane"}
MAIN = {v["nom"].split(" et ")[0]: v for v in B.VILLES}  # textes rédigés à la main
DIAG = {d["slug"]: d for d in DIAGS}
COUL = ["#00A06D", "#52B153", "#A5CC74", "#F4E70F", "#F0B50F", "#EB8235", "#D7221F"]
SRC = '<p class="note">Source : base des DPE de l\'ADEME (logements existants), extraction du 17 novembre 2026. Ces chiffres portent sur les logements ayant fait l\'objet d\'un DPE depuis juillet 2021, et non sur l\'ensemble du parc.</p>'
BTN = f'<p><a class="btn" href="tel:{TEL_LINK}">📞 {TEL}</a> <a class="btn clair" href="/quels-diagnostics/">Quels diagnostics pour mon bien ?</a></p>'

def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")
def zpath(zs): return f"/secteurs/secteur-{zs}/"
def cpath(c): return f"/secteurs/{c['slug']}/"
def pct(a, b): return round(100 * a / b) if b else 0
def nb(n): return f"{n:,}".replace(",", " ")
def a_la(nom): return "au " + nom[3:] if nom.startswith("Le ") else "à " + nom
def de_la(nom):
    if nom.startswith("Le "): return "du " + nom[3:]
    return ("d'" if re.match(r"^[AEIOUYÉÈ]", nom) else "de ") + nom

def charger():
    C = {}
    for l in open(B.SRC + "/ademe_communes.txt", encoding="utf8"):
        if l.startswith("#") or not l.strip(): continue
        f = l.strip().split("|"); i = int(f[0])
        if i in EXCLUS: continue
        v = list(map(int, f[3:]))
        C[i] = dict(i=i, nom=NOMS[i], slug=slug(NOMS[i]), n=int(f[1]), et=list(map(int, f[2].split())), maison=v[0], appart=v[1], elec=v[2], gaz=v[3], fioul=v[4], bois=v[5], reseau=v[6],
                    av48=v[7], p4874=v[8], p7588=v[9], p8905=v[10], p06=v[11])
    for z in ZONES:
        for i in z[4]:
            if i in C: C[i]["zone"] = z
    return C

def somme(cs):
    t = dict(n=0, et=[0] * 7, maison=0, appart=0, elec=0, gaz=0, fioul=0, bois=0, reseau=0, av48=0, p4874=0, p7588=0, p8905=0, p06=0)
    for c in cs:
        for k in t:
            if k == "et": t["et"] = [x + y for x, y in zip(t["et"], c["et"])]
            else: t[k] += c[k]
    return t

def chiffres(d):
    efg = sum(d["et"][4:]); fg = sum(d["et"][5:])
    return dict(efg=efg, fg=fg, pefg=pct(efg, d["n"]), pfg=pct(fg, d["n"]), pmaison=pct(d["maison"], d["n"]), pappart=pct(d["appart"], d["n"]),
                pelec=pct(d["elec"], d["n"]), pgaz=pct(d["gaz"], d["n"]), pfioul=pct(d["fioul"], d["n"]), pav48=pct(d["av48"], d["n"]),
                pav75=pct(d["av48"] + d["p4874"], d["n"]), pav89=pct(d["av48"] + d["p4874"] + d["p7588"], d["n"]))

def barres(d):
    m = max(d["et"]) or 1
    return '<div class="etiq" role="img" aria-label="Répartition des étiquettes DPE">' + "".join(
        f'<div><span class="l" style="background:{COUL[k]};color:{"#fff" if k in (0, 1, 5, 6) else "#1c2733"}">{"ABCDEFG"[k]}</span><span class="b"><i style="width:{max(2, round(100 * x / m))}%;background:{COUL[k]}"></i></span><span class="v">{nb(x)} <small>({pct(x, d["n"])} %)</small></span></div>'
        for k, x in enumerate(d["et"])) + "</div>"

def tuiles(d, k):
    return f"""<div class="chiffres">
<div><b>{nb(d['n'])}</b><span>DPE enregistrés</span></div>
<div><b>{k['pefg']} %</b><span>classés E, F ou G</span></div>
<div><b>{k['pmaison']} %</b><span>de maisons</span></div>
<div><b>{k['pelec']} %</b><span>chauffés à l'électricité</span></div>
<div><b>{k['pav75']} %</b><span>construits avant 1975</span></div>
</div>"""

def analyse(ou, k):
    """Paragraphes rédigés à partir des chiffres réels."""
    L = []
    if k["pmaison"] >= 75: L.append(f"Le parc diagnostiqué {ou} est très majoritairement composé de maisons individuelles ({k['pmaison']} %). Les dossiers de vente y comportent le plus souvent le DPE, les diagnostics électricité et gaz, l'état des risques et, selon l'âge du bien, l'amiante et le plomb.")
    elif k["pappart"] >= 50: L.append(f"Les appartements représentent {k['pappart']} % des logements diagnostiqués {ou}. Le <a href=\"/diagnostics/loi-carrez-boutin/\">mesurage loi Carrez</a> s'ajoute donc très souvent au dossier, et les copropriétés sont concernées par le <a href=\"/diagnostics/pppt/\">PPPT</a> et le <a href=\"/diagnostics/dpe-collectif/\">DPE collectif</a>.")
    else: L.append(f"Le parc diagnostiqué {ou} mêle maisons ({k['pmaison']} %) et appartements ({k['pappart']} %) : selon le bien, le dossier va du simple DPE au dossier complet avec mesurage loi Carrez en copropriété.")
    if k["pav48"] >= 20: L.append(f"{k['pav48']} % des logements diagnostiqués ont été construits avant 1948 : le <a href=\"/diagnostics/plomb/\">diagnostic plomb</a> y est fréquent, et l'<a href=\"/diagnostics/etat-parasitaire/\">état parasitaire</a>, que nous réalisons sur tous les biens, y prend tout son sens.")
    if k["pav89"] >= 55: L.append(f"{k['pav89']} % des logements datent d'avant 1989 : ils sont concernés par le <a href=\"/diagnostics/amiante/\">diagnostic amiante</a>, obligatoire pour tout permis de construire antérieur au 1er juillet 1997.")
    if k["pelec"] >= 55: L.append(f"L'électricité est l'énergie de chauffage principale de {k['pelec']} % des logements. Avec le nouveau coefficient applicable au 1er janvier 2027, une partie d'entre eux va gagner une classe énergétique : <a href=\"/dpe-2027/\">vérifiez-le avec notre simulateur</a>.")
    elif k["pgaz"] >= 40: L.append(f"Le gaz naturel chauffe {k['pgaz']} % des logements diagnostiqués : le <a href=\"/diagnostics/gaz/\">diagnostic gaz</a> est requis dès que l'installation a plus de 15 ans.")
    if k["pfioul"] >= 15: L.append(f"Le fioul reste présent dans {k['pfioul']} % des logements, souvent parmi les plus énergivores : l'<a href=\"/diagnostics/audit-energetique/\">audit énergétique</a> aide à préparer un changement de chauffage.")
    L.append(f"{k['pefg']} % des DPE sont classés E, F ou G ({nb(k['efg'])} logements), dont {k['pfg']} % en F ou G. Les maisons concernées doivent faire l'objet d'un <a href=\"/diagnostics/audit-energetique/\">audit énergétique</a> avant la vente.")
    return "".join(f"<p>{x}</p>" for x in L)

def cartes_diags(): return cartes([(f'/diagnostics/{d["slug"]}/', d["nom"], d["titre"]) for d in DIAGS])
def liens_communes(cs): return ", ".join(f'<a href="{cpath(c)}">{e(c["nom"])}</a>' for c in cs)

QUESTIONNAIRE = """<form id="qd" class="qd" novalidate>
<div><label for="qd-projet">Votre projet</label><select id="qd-projet"><option value="vente">Je vends</option><option value="location">Je loue</option><option value="travaux">Je prépare des travaux</option><option value="copro">Je gère une copropriété</option></select></div>
<div><label for="qd-type">Type de bien</label><select id="qd-type"><option value="maison">Maison</option><option value="appartement">Appartement en copropriété</option><option value="immeuble">Immeuble entier</option></select></div>
<div><label for="qd-annee">Année de construction</label><select id="qd-annee"><option value="av1949">Avant 1949</option><option value="av1997" selected>De 1949 à juin 1997</option><option value="apres">Après juillet 1997</option></select></div>
<div><label for="qd-elec">Installation électrique de plus de 15 ans ?</label><select id="qd-elec"><option value="oui">Oui</option><option value="non">Non</option><option value="nsp">Je ne sais pas</option></select></div>
<div><label for="qd-gaz">Installation de gaz</label><select id="qd-gaz"><option value="aucun">Pas de gaz</option><option value="plus15">Plus de 15 ans</option><option value="moins15">Moins de 15 ans</option><option value="nsp">Je ne sais pas</option></select></div>
<div><label for="qd-classe">Étiquette du DPE actuel</label><select id="qd-classe"><option value="inconnu">Je ne la connais pas</option><option value="abcd">A, B, C ou D</option><option value="efg">E, F ou G</option></select></div>
<div class="qd-btn"><button type="submit" class="btn">Voir mes diagnostics</button></div>
</form>
<div id="qd-res" aria-live="polite"></div>
<noscript><p>Consultez notre <a href="/vente-location/">tableau des diagnostics obligatoires</a>.</p></noscript>
<script src="/assets/quels.js" defer></script>"""

ARTICLES = [
 dict(slug="dpe-2027-coefficient-electricite", date="2026-11-17", titre="DPE 2027 : le coefficient de l'électricité passe à 1,7",
  desc="Au 1er janvier 2027, le coefficient de conversion de l'électricité du DPE passe de 1,9 à 1,7. Ce que cela change pour les logements du Nord-Finistère.",
  corps=lambda k: f"""<p class="chapo">Un arrêté du 19 août 2026 abaisse de 1,9 à 1,7 le coefficient qui convertit l'électricité en énergie primaire dans le DPE et l'audit énergétique. La mesure s'applique au 1er janvier 2027.</p>
<h2>Ce qui change</h2><p>Le DPE exprime la consommation d'un logement en énergie primaire. Pour l'électricité, chaque kilowattheure consommé est multiplié par un coefficient : 2,3 jusqu'en 2025, 1,9 depuis le 1er janvier 2026, puis 1,7 à partir du 1er janvier 2027. La consommation affichée des logements électriques baisse donc mécaniquement, et certains changent de classe.</p>
<h2>Qui est concerné dans le Nord-Finistère ?</h2><p>Dans les communes que nous suivons, {k['pelec']} % des logements diagnostiqués sont chauffés principalement à l'électricité. Ce sont eux qui peuvent gagner une classe. Les logements chauffés au gaz, au fioul ou au bois ne voient leur consommation baisser que marginalement.</p>
<h2>Faut-il refaire son DPE ?</h2><p>Non. Les DPE en cours de validité restent valables. Une attestation officielle de nouvelle étiquette pourra être téléchargée gratuitement sur l'Observatoire DPE-Audit de l'ADEME à partir du 1er janvier 2027, avec le numéro du DPE.</p>
<h2>Connaître dès maintenant votre future étiquette</h2><p>Notre <a href="/dpe-2027/">simulateur DPE 2027</a> calcule l'étiquette estimée à partir du numéro ADEME. Un logement classé G qui passe en F peut de nouveau être loué ; une maison qui sort des classes E, F ou G n'est plus soumise à l'audit énergétique obligatoire à la vente.</p>
<p class="note">Sources : arrêté du 19 août 2026 publié au Journal officiel du 26 août 2026 ; ministère de la Transition écologique ; base des DPE de l'ADEME.</p>"""),
 dict(slug="passoires-thermiques-calendrier-location", date="2026-11-17", titre="Passoires thermiques : le calendrier des interdictions de louer",
  desc="Logements classés G, F puis E : les dates d'interdiction de mise en location et la situation dans le Nord-Finistère.",
  corps=lambda k: f"""<p class="chapo">La loi Climat et résilience retire progressivement du marché locatif les logements les plus énergivores. Voici les échéances et ce qu'elles représentent localement.</p>
<h2>Les dates à retenir</h2>{ul(["Depuis le 1er janvier 2025 : les logements classés G ne peuvent plus être proposés à la location.", "1er janvier 2028 : l'interdiction s'étend aux logements classés F.", "1er janvier 2034 : elle s'étend aux logements classés E."])}<p>Ces échéances s'appliquent aux nouveaux baux, ainsi qu'aux renouvellements et reconductions.</p>
<h2>La situation dans le Nord-Finistère</h2><p>Dans les communes que nous suivons, {k['pfg']} % des DPE enregistrés sont classés F ou G, et {k['pefg']} % sont classés E, F ou G. Le détail commune par commune figure dans notre <a href="/observatoire-dpe-nord-finistere/">observatoire DPE du Nord-Finistère</a>.</p>
<h2>Que faire si votre logement est concerné ?</h2>{ul(["Vérifier d'abord l'étiquette : avec le coefficient applicable au 1er janvier 2027, certains logements électriques changent de classe. <a href=\"/dpe-2027/\">Testez votre DPE</a>.", "Faire réaliser un <a href=\"/diagnostics/audit-energetique/\">audit énergétique</a> pour identifier les travaux les plus efficaces.", "Refaire le <a href=\"/diagnostics/dpe/\">DPE</a> après travaux pour faire constater la nouvelle classe."])}
<p class="note">Sources : loi du 22 août 2021 portant lutte contre le dérèglement climatique ; base des DPE de l'ADEME.</p>"""),
 dict(slug="audit-energetique-vente-maison-classe-e", date="2026-11-17", titre="Audit énergétique : obligatoire pour vendre une maison classée E, F ou G",
  desc="Depuis le 1er janvier 2025, l'audit énergétique est obligatoire pour vendre une maison ou un immeuble en monopropriété classé E. Le point pour le Nord-Finistère.",
  corps=lambda k: f"""<p class="chapo">L'audit énergétique réglementaire accompagne désormais la vente de toutes les maisons et de tous les immeubles en monopropriété classés E, F ou G.</p>
<h2>Le calendrier</h2>{ul(["1er avril 2023 : biens classés F ou G.", "1er janvier 2025 : biens classés E.", "1er janvier 2034 : biens classés D."])}
<h2>Ce que contient l'audit</h2><p>Un état des lieux du bâti et des équipements, puis des scénarios de travaux chiffrés, par étapes ou en une seule fois, avec les gains énergétiques attendus et les aides mobilisables. Il est valable cinq ans et doit être remis au candidat acquéreur dès la première visite.</p>
<h2>Combien de biens concernés localement ?</h2><p>Dans les communes du Nord-Finistère que nous suivons, {nb(k['efg'])} DPE sont classés E, F ou G, soit {k['pefg']} % des DPE enregistrés. Tous ne sont pas des maisons, mais l'ordre de grandeur montre l'ampleur du sujet.</p>
<h2>Un point à vérifier avant de commander</h2><p>Au 1er janvier 2027, le nouveau coefficient de l'électricité fera changer de classe une partie des logements électriques. Une maison qui sort de la classe E n'est plus soumise à l'audit. <a href="/dpe-2027/">Vérifiez avec notre simulateur</a>, puis <a href="/diagnostics/audit-energetique/">consultez notre page audit énergétique</a>.</p>
<p class="note">Sources : loi du 22 août 2021 ; décret et arrêté du 4 mai 2022 relatifs à l'audit énergétique ; base des DPE de l'ADEME.</p>"""),
 dict(slug="pppt-petites-coproprietes", date="2026-11-17", titre="PPPT : les petites copropriétés sont concernées depuis 2025",
  desc="Depuis le 1er janvier 2025, toutes les copropriétés de plus de 15 ans doivent élaborer un projet de plan pluriannuel de travaux, y compris les plus petites.",
  corps=lambda k: f"""<p class="chapo">Longtemps réservée aux grands ensembles, l'obligation d'élaborer un projet de plan pluriannuel de travaux (PPPT) s'applique maintenant à toutes les copropriétés de plus de quinze ans.</p>
<h2>Un calendrier arrivé à son terme</h2>{ul(["1er janvier 2023 : copropriétés de plus de 200 lots.", "1er janvier 2024 : copropriétés de 51 à 200 lots.", "1er janvier 2025 : copropriétés de 50 lots ou moins."])}
<h2>Pourquoi les petites copropriétés sont en retard</h2><p>Dans les centres-bourgs du Nord-Finistère, beaucoup d'immeubles de quelques lots fonctionnent avec un syndic bénévole, voire sans syndic. L'obligation y est souvent méconnue, alors qu'elle conditionne la bonne information des acquéreurs lors de la vente d'un lot.</p>
<h2>Par où commencer ?</h2>{ul(["Faire réaliser le <a href=\"/diagnostics/dpe-collectif/\">DPE collectif</a>, obligatoire pour toutes les copropriétés depuis le 1er janvier 2026.", "Faire établir le <a href=\"/diagnostics/pppt/\">projet de plan pluriannuel de travaux</a> et le présenter en assemblée générale.", "Envisager un <a href=\"/diagnostics/dtg/\">diagnostic technique global</a> si l'immeuble nécessite une analyse plus complète."])}
<p class="note">Sources : loi du 22 août 2021 ; article 14-2 de la loi du 10 juillet 1965.</p>"""),
 dict(slug="radon-finistere-etat-des-risques", date="2026-11-17", titre="Radon dans le Finistère : ce que dit l'état des risques",
  desc="Près de neuf communes du Finistère sur dix sont classées en potentiel radon significatif. Ce que cela implique pour une vente ou une location.",
  corps=lambda k: """<p class="chapo">Le radon est un gaz radioactif naturel issu des sous-sols granitiques. La Bretagne est l'une des régions les plus exposées, et le Finistère en particulier.</p>
<h2>Un département très largement concerné</h2><p>Les communes sont classées en trois zones selon le potentiel radon de leur sol. D'après l'Agence régionale de santé Bretagne, 246 communes du Finistère, soit 88 %, sont classées en zone 3, celle du potentiel significatif.</p>
<h2>Ce que cela change pour une vente ou une location</h2><p>Lorsque le bien se situe en zone 3, l'<a href="/diagnostics/erp/">état des risques</a> remis à l'acquéreur ou au locataire doit le mentionner et être accompagné d'une fiche d'information sur le radon. L'état des risques doit dater de moins de six mois.</p>
<h2>Les bons réflexes</h2><p>Aérer chaque jour, entretenir la ventilation, étanchéifier les passages entre le sous-sol et les pièces de vie. Lors d'une rénovation énergétique, la ventilation doit être traitée en même temps que l'isolation pour ne pas piéger le radon dans le logement.</p>
<p class="note">Sources : Agence régionale de santé Bretagne ; arrêté du 27 juin 2018 délimitant les zones à potentiel radon ; préfecture du Finistère.</p>"""),
 dict(slug="merule-finistere-vente-immobiliere", date="2026-11-17", titre="Mérule dans le Finistère : quelles obligations lors d'une vente ?",
  desc="Dans les communes couvertes par l'arrêté préfectoral mérule, le vendeur doit informer l'acquéreur du risque. Le point pour le Nord-Finistère.",
  corps=lambda k: f"""<p class="chapo">La mérule est un champignon qui se développe dans les bâtiments humides et mal ventilés et qui dégrade les bois de charpente et de plancher. Le climat et le bâti ancien bretons lui sont favorables.</p>
<h2>L'obligation d'information</h2><p>Dans les communes inscrites dans un arrêté préfectoral « mérule », le vendeur doit fournir, au sein du dossier de diagnostic technique, une information sur la présence d'un risque de mérule. Par ailleurs, l'occupant ou le propriétaire qui a connaissance de la présence de mérule dans un immeuble doit en faire la déclaration en mairie.</p>
<h2>L'état parasitaire, une sécurité pour la vente</h2><p>Au-delà de l'information obligatoire, l'<a href="/diagnostics/etat-parasitaire/">état parasitaire</a> recherche concrètement les indices de mérule et d'insectes à larves xylophages. Dans les communes que nous suivons, {k['pav48']} % des logements diagnostiqués datent d'avant 1948 : pour ces biens, c'est une précaution que les notaires et les acquéreurs demandent de plus en plus.</p>
<h2>Votre commune est-elle concernée ?</h2><p>Nous vérifions pour vous, à partir de l'adresse du bien, si un arrêté préfectoral s'applique. Appelez-nous au <a href="tel:{TEL_LINK}">{TEL}</a>.</p>
<p class="note">Sources : articles L. 126-5, L. 126-25 et L. 271-4 du Code de la construction et de l'habitation ; base des DPE de l'ADEME.</p>"""),
]

def L(slug, cond=""):
    d = DIAG[slug]
    return f'<a href="/diagnostics/{slug}/">{e(d["titre"])}</a>' + (f" : {cond}" if cond else "")

PROJETS = [
 dict(slug="vente-maison", nom="Vente d'une maison", h1="Diagnostics immobiliers pour vendre une maison", seo="Diagnostics vente maison",
  intro="Pour vendre une maison, le dossier de diagnostic technique doit être annexé à la promesse de vente, et l'étiquette du DPE doit figurer dès l'annonce. Voici les diagnostics à prévoir.",
  liste=lambda: [L("dpe", "toujours obligatoire, valable 10 ans"), L("erp", "toujours obligatoire, valable 6 mois"), L("amiante", "si le permis de construire est antérieur au 1er juillet 1997"),
                 L("plomb", "si la maison a été construite avant 1949"), L("electricite", "si l'installation a plus de 15 ans"), L("gaz", "si l'installation a plus de 15 ans"),
                 L("audit-energetique", "obligatoire si le DPE classe la maison en E, F ou G"), L("etat-parasitaire", "réalisé sur tous les biens que nous diagnostiquons")],
  stat=lambda d, k, dans: f"Les maisons représentent {k['pmaison']} % des logements diagnostiqués {dans} ({nb(d['maison'])} DPE). {k['pefg']} % des DPE du secteur sont classés E, F ou G : pour ces maisons, l'audit énergétique s'ajoute au dossier de vente.",
  faq=[("Quand faire réaliser les diagnostics ?", "Dès la mise en vente : l'étiquette du DPE est obligatoire dans l'annonce, et l'audit énergétique, s'il est requis, doit être remis dès la première visite."),
       ("Combien de temps dure la visite ?", "Une à deux heures pour une maison, selon la surface, l'âge et le nombre de diagnostics à réaliser.")]),
 dict(slug="vente-appartement", nom="Vente d'un appartement", h1="Diagnostics immobiliers pour vendre un appartement", seo="Diagnostics vente appartement",
  intro="La vente d'un appartement en copropriété ajoute au dossier le mesurage loi Carrez et plusieurs documents propres à l'immeuble. Voici les diagnostics à prévoir pour le lot.",
  liste=lambda: [L("dpe", "toujours obligatoire, valable 10 ans"), L("erp", "toujours obligatoire, valable 6 mois"), L("loi-carrez-boutin", "surface privative loi Carrez, obligatoire en copropriété"),
                 L("amiante", "parties privatives, si le permis de construire est antérieur au 1er juillet 1997"), L("plomb", "si l'immeuble a été construit avant 1949"),
                 L("electricite", "si l'installation a plus de 15 ans"), L("gaz", "si l'installation a plus de 15 ans"), L("etat-parasitaire", "réalisé sur tous les biens que nous diagnostiquons")],
  stat=lambda d, k, dans: f"{nb(d['appart'])} DPE d'appartements sont enregistrés {dans}, soit {k['pappart']} % des logements diagnostiqués. {k['pav75']} % des logements du secteur datent d'avant 1975 : l'amiante et, pour les plus anciens, le plomb sont très souvent au dossier.",
  faq=[("Faut-il un audit énergétique pour un appartement ?", "Non. L'audit énergétique réglementaire à la vente ne concerne que les maisons et les immeubles en monopropriété."),
       ("Quels documents de copropriété sont remis à l'acquéreur ?", "Notamment le carnet d'entretien, le <a href=\"/diagnostics/pppt/\">plan pluriannuel de travaux</a> ou son projet, et le dossier technique amiante des parties communes. Le syndic vous les fournit.")]),
 dict(slug="location", nom="Mise en location", h1="Diagnostics immobiliers pour louer un logement", seo="Diagnostics location",
  intro="Le dossier de diagnostic technique est annexé au bail, vide ou meublé. Le DPE y occupe une place particulière : il conditionne désormais le droit de louer.",
  liste=lambda: [L("dpe", "obligatoire, valable 10 ans ; les logements classés G ne peuvent plus être loués"), L("erp", "obligatoire, valable 6 mois"), L("loi-carrez-boutin", "surface habitable loi Boutin, à mentionner dans le bail"),
                 L("plomb", "si le logement a été construit avant 1949"), L("electricite", "si l'installation a plus de 15 ans, valable 6 ans"), L("gaz", "si l'installation a plus de 15 ans, valable 6 ans"),
                 L("amiante", "dossier amiante des parties privatives, en immeuble collectif d'avant 1997")],
  stat=lambda d, k, dans: f"{k['pfg']} % des DPE enregistrés {dans} sont classés F ou G, et {k['pefg']} % E, F ou G. Les logements G sont déjà exclus de la location, les F le seront en 2028 et les E en 2034. Avec le coefficient applicable au 1er janvier 2027, une partie des logements électriques change de classe : <a href=\"/dpe-2027/\">testez le vôtre</a>.",
  faq=[("Faut-il refaire les diagnostics à chaque locataire ?", "Non, tant qu'ils sont valides. Seul l'état des risques doit avoir moins de six mois à la signature du bail."),
       ("Mon logement est classé F, puis-je encore le louer ?", "Oui jusqu'au 1er janvier 2028. Un <a href=\"/diagnostics/audit-energetique/\">audit énergétique</a> permet d'anticiper les travaux.")]),
 dict(slug="travaux", nom="Avant travaux", h1="Diagnostics avant travaux ou démolition", seo="Diagnostics avant travaux",
  intro="Avant de rénover, de percer ou de démolir, le maître d'ouvrage doit faire rechercher l'amiante dans les parties du bâtiment concernées par le chantier. C'est une obligation qui protège les entreprises, les occupants et vous-même.",
  liste=lambda: [L("amiante", "repérage amiante avant travaux ou avant démolition, obligatoire pour tout bâtiment dont le permis est antérieur au 1er juillet 1997"),
                 L("plomb", "repérage du plomb avant travaux dans les bâtiments d'avant 1949, pour protéger les intervenants"),
                 L("audit-energetique", "pour choisir et hiérarchiser les travaux de rénovation énergétique"), L("dpe", "après travaux, pour faire constater la nouvelle étiquette"),
                 L("etat-parasitaire", "avant d'intervenir sur une charpente ou un plancher ancien")],
  stat=lambda d, k, dans: f"{k['pav89']} % des logements diagnostiqués {dans} ont été construits avant 1989, et {k['pav48']} % avant 1948. La grande majorité des chantiers de rénovation du secteur porte donc sur des bâtiments susceptibles de contenir de l'amiante.",
  faq=[("Le diagnostic amiante de la vente suffit-il avant des travaux ?", "Non. Le repérage avant travaux est une mission différente, ciblée sur les zones du chantier, avec des sondages destructifs."),
       ("Qui doit commander le repérage ?", "Le donneur d'ordre des travaux : le propriétaire, le maître d'ouvrage ou le syndic pour les parties communes.")]),
]


# ---------------------------------------------------------------- maillage interne
PRINC = ["Lesneven", "Brest", "Plabennec", "Landerneau", "Landivisiau", "Lannilis", "Saint-Pol-de-Léon", "Saint-Renan", "Morlaix"]
ART_DIAG = {  # articles liés à chaque prestation
 "dpe": ["dpe-2027-coefficient-electricite", "passoires-thermiques-calendrier-location"],
 "audit-energetique": ["audit-energetique-vente-maison-classe-e", "dpe-2027-coefficient-electricite"],
 "pppt": ["pppt-petites-coproprietes"], "dtg": ["pppt-petites-coproprietes"], "dpe-collectif": ["pppt-petites-coproprietes"],
 "erp": ["radon-finistere-etat-des-risques"], "etat-parasitaire": ["merule-finistere-vente-immobiliere"], "plomb": ["merule-finistere-vente-immobiliere"],
 "electricite": ["passoires-thermiques-calendrier-location"], "gaz": ["passoires-thermiques-calendrier-location"], "loi-carrez-boutin": ["pppt-petites-coproprietes"],
}
ART_SERVICE = {  # prestation localisée mise en avant dans chaque article
 "dpe-2027-coefficient-electricite": "dpe", "passoires-thermiques-calendrier-location": "dpe", "audit-energetique-vente-maison-classe-e": "audit-energetique",
 "pppt-petites-coproprietes": "pppt", "radon-finistere-etat-des-risques": None, "merule-finistere-vente-immobiliere": None,
}
def cartes_art(slugs):
    a = {x["slug"]: x for x in ARTICLES}
    return cartes([("/actualites/" + x + "/", a[x]["titre"], a[x]["desc"]) for x in slugs])
def liens_art(slugs):
    a = {x["slug"]: x for x in ARTICLES}
    return ul([f'<a href="/actualites/{x}/">{e(a[x]["titre"])}</a>' for x in slugs])
def liens_princ(): return ", ".join(f'<a href="/secteurs/{slug(n)}/">{e(n)}</a>' for n in PRINC)
def projets_de(s): return [p for p in PROJETS if any(f"/diagnostics/{s}/" in x for x in p["liste"]())]
def autres_zones(prefixe, zs): return ", ".join(f'<a href="{prefixe}{z[0]}/">{e(z[1])}</a>' for z in ZONES if z[0] != zs)

def extra_diag(s):
    """Bas des pages prestations : secteurs, villes, projets et articles liés."""
    D = DIAG[s]
    if s in SERVICES_ZONE:
        h = f'<h2>{e(D["nom"])} : où nous intervenons</h2>' + cartes([(f"/diagnostics/{s}/{z[0]}/", f'{D["nom"]} – {z[1]}', f'{D["titre"]} {z[3]}') for z in ZONES])
    else:
        h = f'<h2>{e(D["nom"])} : où nous intervenons</h2>' + cartes([(zpath(z[0]), z[2], "Diagnostics immobiliers " + z[3]) for z in ZONES])
    h += f'<p>Villes principales : {liens_princ()}. <a href="/secteurs/">Voir toutes les communes desservies</a>.</p>'
    ps = projets_de(s)
    if ps: h += "<h2>Selon votre projet</h2>" + cartes([(f"/projets/{p['slug']}/", p["nom"], p["h1"]) for p in ps])
    if ART_DIAG.get(s): h += "<h2>À lire sur ce sujet</h2>" + cartes_art(ART_DIAG[s])
    return h

# ---------------------------------------------------------------- contenu local tiré des données ADEME
PERIODES = [("av48", "Avant 1948"), ("p4874", "De 1948 à 1974"), ("p7588", "De 1975 à 1988"), ("p8905", "De 1989 à 2005"), ("p06", "Depuis 2006")]
ENERGIES = [("elec", "électricité"), ("gaz", "gaz"), ("fioul", "fioul"), ("bois", "bois"), ("reseau", "réseau de chaleur")]
def table_periodes(c):
    rows = "".join(f'<tr><th scope="row">{l}</th><td>{nb(c[k])}</td><td>{pct(c[k], c["n"])} %</td></tr>' for k, l in PERIODES)
    return f'<div class="defile"><table><thead><tr><th scope="col">Période de construction</th><th scope="col">DPE enregistrés</th><th scope="col">Part</th></tr></thead><tbody>{rows}</tbody></table></div>'
RESEAU_A_CONFIRMER = {"Saint-Pol-de-Léon"}  # part « réseau de chaleur » de la base à confirmer avant affichage
def phrase_energies(c, ou):
    parts = sorted(((pct(c[k], c["n"]), l) for k, l in ENERGIES if pct(c[k], c["n"]) >= 1 and not (k == "reseau" and c["nom"] in RESEAU_A_CONFIRMER)), reverse=True)
    return f'<p>Énergie de chauffage principale des logements diagnostiqués {ou} : ' + ", ".join(f"{l} {p} %" for p, l in parts) + ".</p>"
INDIC = [("pefg", "Classés E, F ou G"), ("pfg", "Classés F ou G"), ("pmaison", "Maisons"), ("pelec", "Chauffage électrique"), ("pgaz", "Chauffage au gaz"), ("pav48", "Construits avant 1948"), ("pav75", "Construits avant 1975")]
def table_compar(nom, k, zlib, kz, kt):
    rows = "".join(f'<tr><th scope="row">{l}</th><td>{k[i]} %</td><td>{kz[i]} %</td><td>{kt[i]} %</td></tr>' for i, l in INDIC)
    return f'<div class="defile"><table><thead><tr><th scope="col">Indicateur</th><th scope="col">{e(nom)}</th><th scope="col">{e(zlib)}</th><th scope="col">Nord-Finistère</th></tr></thead><tbody>{rows}</tbody></table></div>'
def phrase_compar(nom, k, kt):
    d = k["pefg"] - kt["pefg"]
    if d >= 3: a = f"La part de logements classés E, F ou G y dépasse de {d} points la moyenne des communes que nous suivons ({kt['pefg']} %)."
    elif d <= -3: a = f"La part de logements classés E, F ou G y est inférieure de {-d} points à la moyenne des communes que nous suivons ({kt['pefg']} %)."
    else: a = f"La part de logements classés E, F ou G y est proche de la moyenne des communes que nous suivons ({kt['pefg']} %)."
    d2 = k["pelec"] - kt["pelec"]
    b = f" Le chauffage électrique y est {'plus' if d2 > 0 else 'moins'} répandu ({k['pelec']} % contre {kt['pelec']} %)." if abs(d2) >= 3 else ""
    return f"<p>{a}{b}</p>"
def articles_pour(k):
    """Articles les plus utiles selon le profil de la commune."""
    L = []
    if k["pelec"] >= 50: L.append("dpe-2027-coefficient-electricite")
    if k["pefg"] >= 25: L.append("audit-energetique-vente-maison-classe-e")
    if k["pfg"] >= 8: L.append("passoires-thermiques-calendrier-location")
    if k["pappart"] >= 25: L.append("pppt-petites-coproprietes")
    if k["pav48"] >= 15: L.append("merule-finistere-vente-immobiliere")
    L.append("radon-finistere-etat-des-risques")
    return L
def secteur_local(z):
    zs = z[0]
    return (f'<h2>Nos prestations {z[3]}</h2>' + cartes([(f"/diagnostics/{s}/{zs}/", DIAG[s]["nom"] + " – " + z[1], DIAG[s]["titre"] + " " + z[3]) for s in SERVICES_ZONE])
            + "<p>Selon votre projet : " + ", ".join(f'<a href="/projets/{p["slug"]}/{zs}/">{p["nom"][0].lower() + p["nom"][1:]}</a>' for p in PROJETS) + ".</p>")

# ---------------------------------------------------------------- pages locales prioritaires : contenu rédigé, chiffres issus des données
def _lesneven(c, k, kt, tout):
    haut = f"""<h2>Une agence sur place, en centre-ville</h2>
<p>Notre agence se trouve au {B.RUE}, à Lesneven. Elle est ouverte du lundi au vendredi, de 9h à 12h et de 14h à 18h : vous pouvez y déposer vos documents (factures de travaux, plans, anciens diagnostics) et y régler votre diagnostic. <a href="/contact/">Coordonnées et itinéraire</a> · <a href="/agence/">Découvrir l'équipe</a>.</p>"""
    bas = f"""<h2>Vendre ou louer à Lesneven : ce qui revient le plus souvent</h2>
{ul([f'<strong>Presque autant d\'appartements que de maisons.</strong> {k["pappart"]} % des logements diagnostiqués sont des appartements. En copropriété, le <a href="/diagnostics/loi-carrez-boutin/">mesurage loi Carrez</a> s\'ajoute au dossier de vente, et l\'immeuble relève du <a href="/diagnostics/pppt/lesneven/">projet de plan pluriannuel de travaux</a> dès qu\'il a plus de quinze ans.',
     f'<strong>Un centre ancien.</strong> {k["pav48"]} % des logements diagnostiqués ont été construits avant 1948 : pour un bien d\'avant 1949, le <a href="/diagnostics/plomb/">diagnostic plomb</a> est obligatoire à la vente comme à la location.',
     f'<strong>Le gaz bien présent.</strong> {k["pgaz"]} % des logements sont chauffés au gaz : le <a href="/diagnostics/gaz/">diagnostic gaz</a> est requis dès que l\'installation a plus de quinze ans.',
     f'<strong>{nb(k["efg"])} DPE classés E, F ou G</strong>, soit {k["pefg"]} % : pour une maison, l\'<a href="/diagnostics/audit-energetique/lesneven/">audit énergétique</a> s\'ajoute au dossier de vente ; pour une location, le <a href="/actualites/passoires-thermiques-calendrier-location/">calendrier des interdictions de louer</a> s\'applique.'])}"""
    faq = [("Où se trouve votre agence à Lesneven ?", f"Au {B.RUE}, {B.CP} {B.VILLE}. Elle est ouverte du lundi au vendredi, de 9h à 12h et de 14h à 18h. Téléphone : {TEL}."),
           ("Ma maison du centre de Lesneven date d'avant 1949 : quels diagnostics en plus ?", "Le constat de risque d'exposition au plomb (CREP) s'ajoute au DPE, à l'état des risques et au diagnostic amiante. Les diagnostics électricité et gaz sont requis si les installations ont plus de quinze ans."),
           ("Faut-il un DPE pour louer un appartement à Lesneven ?", "Oui. Le DPE est obligatoire pour toute mise en location et il doit figurer dans l'annonce. Les logements classés G ne peuvent plus être proposés à la location depuis le 1er janvier 2025.")]
    return haut, bas, faq

def _brest(c, k, kt, tout):
    metro = ["Guipavas", "Le Relecq-Kerhuon", "Gouesnou", "Bohars", "Guilers", "Plouzané", "Plougastel-Daoulas"]
    haut = f"""<h2>Votre diagnostiqueur immobilier à Brest</h2>
<p>Nos diagnostiqueurs certifiés se déplacent à Brest et dans la métropole ({", ".join(f'<a href="/secteurs/{slug(n)}/">{e(n)}</a>' for n in metro)}) pour les ventes, les locations, les travaux et les copropriétés. Le rendez-vous se prend par téléphone auprès de notre agence de Lesneven, et les rapports vous sont envoyés par e-mail.</p>"""
    part_app = pct(c["appart"], tout["appart"])
    bas = f"""<h2>Un parc d'appartements hérité de la reconstruction</h2>
<p>{pct(c["p4874"], c["n"])} % des logements diagnostiqués à Brest ont été construits entre 1948 et 1974, années de la reconstruction du centre-ville puis des grands ensembles, et {k["pappart"]} % sont des appartements. Pour une vente, cela se traduit ainsi :</p>
{ul(['<strong>Amiante</strong> : le <a href="/diagnostics/amiante/">diagnostic amiante</a> des parties privatives est requis dès que le permis de construire est antérieur au 1er juillet 1997, ce qui est le cas de la grande majorité des immeubles brestois.',
     '<strong>Loi Carrez</strong> : le <a href="/diagnostics/loi-carrez-boutin/">mesurage</a> est obligatoire pour tout lot de copropriété.',
     f'<strong>Plomb</strong> : il ne concerne que les logements d\'avant 1949, soit une minorité du parc diagnostiqué ({k["pav48"]} % construits avant 1948).',
     f'<strong>Audit énergétique</strong> : il ne s\'applique pas aux appartements. Seules les maisons ({k["pmaison"]} % des logements diagnostiqués) et les immeubles en monopropriété classés E, F ou G y sont soumis : <a href="/diagnostics/audit-energetique/brest/">audit énergétique à Brest</a>.'])}
<h2>Gaz et réseau de chaleur : deux particularités brestoises</h2>
<p>{k["pgaz"]} % des logements diagnostiqués à Brest sont chauffés au gaz : le <a href="/diagnostics/gaz/">diagnostic gaz</a> est requis dès que l'installation intérieure a plus de quinze ans. {pct(c["reseau"], c["n"])} % sont raccordés à un réseau de chaleur : dans ce cas, le DPE tient compte des caractéristiques du réseau et de l'installation collective, et les documents remis par le syndic sont utiles le jour de la visite.</p>
<p>Le chauffage électrique ne concerne que {k["pelec"]} % des logements, contre {kt["pelec"]} % dans l'ensemble des communes que nous suivons : le changement de coefficient du 1er janvier 2027 y fera donc évoluer moins d'étiquettes qu'ailleurs. <a href="/diagnostics/dpe/brest/">Le DPE à Brest en détail</a>.</p>
<h2>Copropriétés brestoises : PPPT, DTG et DPE collectif</h2>
<p>Avec {nb(c["appart"])} DPE d'appartements enregistrés, Brest rassemble {part_app} % des appartements diagnostiqués dans les {tout["nbc"]} communes que nous suivons. Toute copropriété de plus de quinze ans doit aujourd'hui disposer d'un <a href="/diagnostics/pppt/brest/">projet de plan pluriannuel de travaux</a>, qui s'appuie sur le <a href="/diagnostics/dpe-collectif/">DPE collectif</a> de l'immeuble ; le <a href="/diagnostics/dtg/brest/">diagnostic technique global</a> va plus loin lorsque l'immeuble le justifie. Nous réalisons ces missions avec un bureau d'études structure et thermique partenaire.</p>"""
    faq = [("Quels diagnostics pour vendre un appartement à Brest ?", "Le DPE, l'état des risques et le mesurage loi Carrez dans tous les cas. S'y ajoutent l'amiante si le permis de construire est antérieur au 1er juillet 1997, l'électricité et le gaz si les installations ont plus de quinze ans, et le plomb si l'immeuble date d'avant 1949. Nous réalisons aussi l'état parasitaire sur tous les biens."),
           ("Faut-il un audit énergétique pour vendre un appartement à Brest ?", "Non. L'audit énergétique réglementaire ne concerne que les maisons individuelles et les immeubles en monopropriété classés E, F ou G."),
           ("Votre agence est à Lesneven : vous déplacez-vous à Brest ?", f"Oui, nous intervenons chaque semaine à Brest et dans sa métropole. Appelez-nous au {TEL} pour convenir d'un rendez-vous.")]
    return haut, bas, faq

def _plabennec(c, k, kt, tout):
    haut = ""
    bas = f"""<h2>Une commune de maisons : ce que cela change pour vos diagnostics</h2>
<p>{k["pmaison"]} % des logements diagnostiqués à Plabennec sont des maisons. {pct(c["p4874"] + c["p7588"], c["n"])} % ont été construits entre 1948 et 1988, et {pct(c["p06"], c["n"])} % depuis 2006.</p>
{ul([f'<strong>Maison classée E, F ou G</strong> : l\'audit énergétique est obligatoire pour la vendre. {nb(k["efg"])} DPE sont dans ce cas à Plabennec, soit {k["pefg"]} % contre {kt["pefg"]} % dans l\'ensemble des communes que nous suivons. <a href="/diagnostics/audit-energetique/abers/">L\'audit énergétique dans le secteur de Plabennec</a>.',
     f'<strong>Chauffage électrique</strong> ({k["pelec"]} % des logements) : avec le coefficient applicable au 1er janvier 2027, une maison peut changer de classe et sortir de l\'obligation d\'audit. <a href="/dpe-2027/">Vérifiez-le avant de commander</a>.',
     f'<strong>Chauffage au fioul</strong> ({k["pfioul"]} % des logements) : ce sont souvent les étiquettes les plus basses. L\'audit chiffre le remplacement de la chaudière et les travaux d\'isolation à mener en priorité.',
     '<strong>Maison construite avant juillet 1997</strong> : le <a href="/diagnostics/amiante/">diagnostic amiante</a> est requis pour la vente.',
     '<strong>Maison des années 2000</strong> : pas d\'amiante ni de plomb à prévoir, mais une installation électrique ou de gaz posée avant 2011 a désormais plus de quinze ans : les diagnostics <a href="/diagnostics/electricite/">électricité</a> et <a href="/diagnostics/gaz/">gaz</a> deviennent obligatoires.'])}"""
    faq = [("Ma maison de Plabennec est classée E : un audit énergétique est-il obligatoire pour la vendre ?", "Oui. Depuis le 1er janvier 2025, l'audit énergétique est obligatoire pour vendre une maison classée E, comme c'était déjà le cas pour les classes F et G. Il est valable cinq ans et doit être remis à l'acquéreur dès la première visite."),
           ("Ma maison est chauffée à l'électricité : son étiquette va-t-elle changer en 2027 ?", "C'est possible : le coefficient de l'électricité passe de 1,9 à 1,7 au 1er janvier 2027. <a href=\"/dpe-2027/\">Notre simulateur</a> estime la nouvelle étiquette à partir du numéro ADEME de votre DPE."),
           ("Ma maison date de 2008 : quels diagnostics pour la vendre ?", "Le DPE et l'état des risques, ainsi que les diagnostics électricité et gaz puisque les installations ont plus de quinze ans. Ni l'amiante ni le plomb ne sont requis. Nous réalisons aussi l'état parasitaire sur tous les biens.")]
    return haut, bas, faq


# ---------------------------------------------------------------- demandes de devis avec origine
from urllib.parse import quote
def devis_mailto(origine):
    sujet = f"Demande de devis diagnostic immobilier - {origine}"
    corps = ("Bonjour,\r\n\r\nJe souhaite un devis pour :\r\n- Projet (vente / location / travaux / copropriété) :\r\n- Type de bien (maison / appartement / immeuble) :\r\n"
             "- Adresse du bien :\r\n- Surface approximative :\r\n- Année de construction :\r\n- Chauffage (électricité / gaz / autre) :\r\n\r\nMes coordonnées :\r\n- Nom :\r\n- Téléphone :\r\n\r\n"
             f"(Demande envoyée depuis la page {origine} du site www.sas-liberge.fr)\r\n")
    return f"mailto:{MAIL}?subject={quote(sujet)}&amp;body={quote(corps)}"
def devis_p(libelle, origine):
    return f'<p><a class="btn clair" href="{devis_mailto(origine)}">{e(libelle)}</a> <a href="/devis/">Comment se passe un devis ?</a></p>'
def echantillon(c, ou):
    """Rappel de l'échantillon et de la période, à placer en tête des sections rédigées."""
    return f"Sur les {nb(c['n'])} DPE enregistrés {ou} entre juillet 2021 et le 17 novembre 2026"
LIMITE = "Ces chiffres décrivent les logements qui ont fait l'objet d'un DPE sur cette période, et non l'ensemble du parc de la commune."

def _morlaix(c, k, kt, tout):
    bas = f"""<h2>Vendre un logement ancien à Morlaix : les diagnostics qui s'ajoutent</h2>
<p>{echantillon(c, "à Morlaix")}, {k["pav48"]} % concernent des logements construits avant 1948, contre {kt["pav48"]} % dans l'ensemble des communes que nous suivons. {LIMITE} Ils indiquent en revanche ce que contiennent le plus souvent les dossiers de vente :</p>
{ul(['le <a href="/diagnostics/plomb/">constat de risque d\'exposition au plomb</a>, obligatoire pour tout logement construit avant 1949, à la vente comme à la location ;',
     'le <a href="/diagnostics/amiante/">diagnostic amiante</a>, requis dès que le permis de construire est antérieur au 1er juillet 1997 ;',
     'l\'<a href="/diagnostics/etat-parasitaire/">état parasitaire</a>, que nous réalisons sur tous les biens et qui prend tout son sens dans les immeubles anciens. Voir aussi notre article sur <a href="/actualites/merule-finistere-vente-immobiliere/">la mérule lors d\'une vente</a>.'])}
<h2>Trois logements diagnostiqués sur quatre sont des appartements</h2>
<p>Les appartements représentent {k["pappart"]} % des DPE enregistrés à Morlaix. Pour la vente d'un lot, le <a href="/diagnostics/loi-carrez-boutin/">mesurage loi Carrez</a> est obligatoire. Côté immeuble, toute copropriété de plus de quinze ans relève du <a href="/diagnostics/pppt/morlaix/">projet de plan pluriannuel de travaux</a>, y compris les petits immeubles gérés par un syndic bénévole ; le <a href="/diagnostics/dtg/morlaix/">diagnostic technique global</a> s'adresse aux immeubles qui demandent une analyse plus complète.</p>
<h2>Le gaz, première énergie de chauffage des logements diagnostiqués</h2>
<p>{k["pgaz"]} % des logements diagnostiqués à Morlaix sont chauffés au gaz : le <a href="/diagnostics/gaz/">diagnostic gaz</a> est requis dès que l'installation intérieure a plus de quinze ans. Le chauffage électrique ne concerne que {k["pelec"]} % des logements : le changement de coefficient du 1er janvier 2027 y modifiera moins d'étiquettes que dans les communes plus électriques. <a href="/diagnostics/dpe/morlaix/">Le DPE à Morlaix et autour de sa baie</a>.</p>
<h2>Logements classés E, F ou G : audit à la vente, calendrier à la location</h2>
<p>{nb(k["efg"])} DPE sont classés E, F ou G à Morlaix, soit {k["pefg"]} % contre {kt["pefg"]} % dans l'ensemble des communes que nous suivons ; {k["pfg"]} % sont en F ou G. Pour une maison, l'<a href="/diagnostics/audit-energetique/morlaix/">audit énergétique</a> s'ajoute au dossier de vente. Pour une location, le <a href="/actualites/passoires-thermiques-calendrier-location/">calendrier des interdictions de louer</a> s'applique.</p>"""
    faq = [("Quels diagnostics pour vendre un appartement ancien à Morlaix ?", "Le DPE, l'état des risques et le mesurage loi Carrez dans tous les cas. S'y ajoutent le plomb si l'immeuble date d'avant 1949, l'amiante si le permis de construire est antérieur au 1er juillet 1997, et les diagnostics électricité et gaz si les installations ont plus de quinze ans. Nous réalisons aussi l'état parasitaire sur tous les biens."),
           ("Notre petit immeuble de Morlaix est géré par un syndic bénévole : sommes-nous concernés par le PPPT ?", "Oui. Depuis le 1er janvier 2025, toutes les copropriétés de plus de quinze ans doivent faire établir un projet de plan pluriannuel de travaux, quelle que soit leur taille et que le syndic soit professionnel ou bénévole."),
           ("Votre agence est à Lesneven : intervenez-vous à Morlaix ?", f"Oui, nous intervenons à Morlaix et dans les communes de sa baie. Appelez-nous au {TEL} pour convenir d'un rendez-vous.")]
    return "", bas, faq

def _landerneau(c, k, kt, tout):
    bas = f"""<h2>Appartement ou maison : deux dossiers différents à Landerneau</h2>
<p>{echantillon(c, "à Landerneau")}, {k["pappart"]} % portent sur des appartements et {k["pmaison"]} % sur des maisons. {LIMITE}</p>
<p><strong>Vous vendez un appartement.</strong> Le <a href="/diagnostics/loi-carrez-boutin/">mesurage loi Carrez</a> est obligatoire, tout comme le <a href="/diagnostics/amiante/">diagnostic amiante</a> des parties privatives si le permis de construire est antérieur au 1er juillet 1997. L'audit énergétique ne s'applique pas aux appartements.</p>
<p><strong>Vous vendez une maison.</strong> Le dossier comprend le DPE, l'état des risques, l'amiante et le plomb selon l'âge du bien, l'électricité et le gaz si les installations ont plus de quinze ans. Si le DPE classe la maison en E, F ou G, l'<a href="/diagnostics/audit-energetique/landerneau/">audit énergétique</a> est obligatoire.</p>
<h2>Des immeubles des années 1950 à 1970</h2>
<p>{pct(c["p4874"], c["n"])} % des logements diagnostiqués à Landerneau ont été construits entre 1948 et 1974. Pour ces immeubles, le dossier technique amiante des parties communes est tenu par le syndic, et la copropriété relève du <a href="/diagnostics/pppt/landerneau/">projet de plan pluriannuel de travaux</a>, qui s'appuie sur le <a href="/diagnostics/dpe-collectif/">DPE collectif</a>. Le <a href="/diagnostics/dtg/landerneau/">diagnostic technique global</a> peut être décidé en assemblée générale pour préparer un programme de travaux.</p>
<h2>Moins de logements classés E, F ou G que la moyenne</h2>
<p>{k["pefg"]} % des DPE enregistrés à Landerneau sont classés E, F ou G ({nb(k["efg"])} DPE), contre {kt["pefg"]} % dans l'ensemble des communes que nous suivons. {pct(c["p06"], c["n"])} % des logements diagnostiqués ont été construits depuis 2006. Le gaz est l'énergie de chauffage de {k["pgaz"]} % des logements : le <a href="/diagnostics/gaz/">diagnostic gaz</a> s'ajoute au dossier dès que l'installation a plus de quinze ans. <a href="/diagnostics/dpe/landerneau/">Le DPE à Landerneau et dans le pays de Daoulas</a>.</p>"""
    faq = [("Je vends une maison classée D à Landerneau : faut-il un audit énergétique ?", "Non. L'audit énergétique n'est obligatoire que pour les maisons et les immeubles en monopropriété classés E, F ou G. Les biens classés D seront concernés à partir du 1er janvier 2034."),
           ("Notre copropriété de Landerneau date des années 1960 : quels diagnostics collectifs prévoir ?", "Le projet de plan pluriannuel de travaux, obligatoire pour toute copropriété de plus de quinze ans, et le DPE collectif. Le dossier technique amiante des parties communes doit par ailleurs être tenu à jour par le syndic."),
           ("Quels diagnostics pour louer un logement à Landerneau ?", "Le DPE, l'état des risques et la surface habitable, auxquels s'ajoutent le plomb si le logement date d'avant 1949 et les diagnostics électricité et gaz si les installations ont plus de quinze ans.")]
    return "", bas, faq

def _landivisiau(c, k, kt, tout):
    lignes = [("Maison construite avant 1949", "DPE, état des risques, plomb, amiante ; électricité et gaz si les installations ont plus de quinze ans ; audit énergétique si le DPE est classé E, F ou G"),
              ("Maison construite de 1949 à juin 1997", "DPE, état des risques, amiante ; électricité et gaz si les installations ont plus de quinze ans ; audit énergétique si le DPE est classé E, F ou G"),
              ("Maison dont le permis est postérieur à juillet 1997", "DPE, état des risques ; électricité et gaz si les installations ont plus de quinze ans ; audit énergétique si le DPE est classé E, F ou G"),
              ("Appartement en copropriété", "DPE, état des risques, mesurage loi Carrez ; amiante si le permis est antérieur à juillet 1997 ; plomb si l'immeuble date d'avant 1949 ; électricité et gaz si les installations ont plus de quinze ans")]
    tab = '<div class="defile"><table><thead><tr><th scope="col">Votre bien</th><th scope="col">Diagnostics à prévoir pour une vente</th></tr></thead><tbody>' + "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in lignes) + "</tbody></table></div>"
    autour = ["Plouvorn", "Bodilis", "Lampaul-Guimiliau", "Plounéventer", "Plouzévédé", "Sizun"]
    bas = f"""<h2>Maison ou appartement : la liste pour une vente à Landivisiau</h2>
<p>{echantillon(c, "à Landivisiau")}, {k["pmaison"]} % concernent des maisons et {k["pappart"]} % des appartements. {LIMITE} Les deux cas se présentent donc aussi souvent l'un que l'autre :</p>
{tab}
<p class="note">Nous réalisons en plus l'<a href="/diagnostics/etat-parasitaire/">état parasitaire</a> sur tous les biens. Liste indicative : <a href="/quels-diagnostics/">obtenez la vôtre en six questions</a>.</p>
<h2>Électricité, gaz, fioul : ce que le chauffage change</h2>
{ul([f'<strong>Électricité ({k["pelec"]} % des logements diagnostiqués)</strong> : avec le coefficient applicable au 1er janvier 2027, une partie de ces logements changera de classe. <a href="/dpe-2027/">Vérifiez le vôtre avec le simulateur</a>.',
     f'<strong>Gaz ({k["pgaz"]} %)</strong> : le <a href="/diagnostics/gaz/">diagnostic gaz</a> est requis dès que l\'installation a plus de quinze ans.',
     f'<strong>Fioul ({k["pfioul"]} %)</strong> : pour une maison classée E, F ou G, l\'<a href="/diagnostics/audit-energetique/landivisiau/">audit énergétique</a> chiffre le remplacement du chauffage et les travaux d\'isolation.'])}
<h2>{nb(k["efg"])} DPE classés E, F ou G</h2>
<p>Cela représente {k["pefg"]} % des DPE enregistrés à Landivisiau, un niveau proche de l'ensemble des communes que nous suivons ({kt["pefg"]} %). Pour les copropriétés, voir aussi le <a href="/diagnostics/pppt/landivisiau/">PPPT</a> et le <a href="/diagnostics/dtg/landivisiau/">DTG</a> dans le secteur de Landivisiau. <a href="/diagnostics/dpe/landivisiau/">Le DPE à Landivisiau et dans son secteur</a>.</p>"""
    faq = [("Ma maison de Landivisiau est chauffée au fioul : qu'en dira le DPE ?", "L'étiquette dépend autant de l'isolation et des équipements que de l'énergie utilisée. Le fioul pèse surtout sur le volet émissions de gaz à effet de serre. Si la maison est classée E, F ou G, l'audit énergétique obligatoire à la vente chiffre le changement de chauffage."),
           ("Intervenez-vous dans les communes autour de Landivisiau ?", "Oui, notamment à " + ", ".join(f'<a href="/secteurs/{slug(n)}/">{n}</a>' for n in autour) + "."),
           ("Quels diagnostics pour louer un appartement à Landivisiau ?", "Le DPE, l'état des risques et la surface habitable. S'y ajoutent le plomb pour un immeuble d'avant 1949, et les diagnostics électricité et gaz si les installations ont plus de quinze ans.")]
    return "", bas, faq

def _saintpol(c, k, kt, tout):
    autour = ["Roscoff", "Plouescat", "Cléder", "Plouénan"]
    bas = f"""<h2>Plus d'un DPE sur quatre classé E, F ou G</h2>
<p>{echantillon(c, "à Saint-Pol-de-Léon")}, {nb(k["efg"])} sont classés E, F ou G, soit {k["pefg"]} % contre {kt["pefg"]} % dans l'ensemble des communes que nous suivons ; {k["pfg"]} % sont en F ou G. {LIMITE}</p>
{ul(['<strong>Pour une vente</strong> : si le bien est une maison, l\'<a href="/diagnostics/audit-energetique/haut-leon/">audit énergétique</a> est obligatoire et doit être remis dès la première visite.',
     '<strong>Pour une location</strong> : les logements classés G ne peuvent plus être proposés à la location depuis le 1er janvier 2025 ; les logements classés F suivront au 1er janvier 2028. <a href="/actualites/passoires-thermiques-calendrier-location/">Le calendrier complet</a>.'])}
<h2>Avant de commander un audit, vérifiez l'effet du coefficient 2027</h2>
<p>{k["pelec"]} % des logements diagnostiqués à Saint-Pol-de-Léon sont chauffés à l'électricité. Au 1er janvier 2027, le coefficient de conversion de l'électricité passe de 1,9 à 1,7 : un logement électrique peut changer de classe sans travaux, et une maison qui sort de la classe E n'est plus soumise à l'audit. <a href="/dpe-2027/">Notre simulateur</a> estime la nouvelle étiquette à partir du numéro ADEME. <a href="/diagnostics/dpe/haut-leon/">Le DPE dans le Haut-Léon</a>.</p>
<h2>Un logement diagnostiqué sur quatre date d'avant 1948</h2>
<p>{k["pav48"]} % des DPE enregistrés portent sur des logements construits avant 1948. Pour ces biens, le <a href="/diagnostics/plomb/">diagnostic plomb</a> est obligatoire (logements d'avant 1949) et le <a href="/diagnostics/amiante/">diagnostic amiante</a> s'ajoute au dossier de vente. Nous réalisons l'<a href="/diagnostics/etat-parasitaire/">état parasitaire</a> sur tous les biens. Les copropriétés de plus de quinze ans relèvent du <a href="/diagnostics/pppt/haut-leon/">PPPT</a>, voire du <a href="/diagnostics/dtg/haut-leon/">DTG</a>.</p>"""
    faq = [("Ma maison de Saint-Pol-de-Léon est classée F : puis-je la vendre ?", "Oui. La vente d'un bien classé F ou G n'est pas interdite, mais l'audit énergétique est obligatoire et doit être remis à l'acquéreur dès la première visite. C'est la mise en location qui est encadrée : les logements classés F ne pourront plus être loués à partir du 1er janvier 2028."),
           ("Mon logement chauffé à l'électricité peut-il changer de classe en 2027 ?", "C'est possible, sans que ce soit systématique. <a href=\"/dpe-2027/\">Notre simulateur</a> donne une estimation à partir du numéro ADEME ; l'attestation officielle sera délivrée par l'ADEME à partir du 1er janvier 2027."),
           ("Intervenez-vous aussi à Roscoff, Plouescat et Cléder ?", "Oui, dans tout le Haut-Léon : " + ", ".join(f'<a href="/secteurs/{slug(n)}/">{n}</a>' for n in autour) + ".")]
    return "", bas, faq

def _saintrenan(c, k, kt, tout):
    recent = pct(c["p8905"] + c["p06"], c["n"]); recent_t = pct(tout["p8905"] + tout["p06"], tout["n"])
    autour = ["Ploudalmézeau", "Le Conquet", "Plouarzel", "Locmaria-Plouzané", "Milizac-Guipronvel"]
    bas = f"""<h2>Un parc plus récent que la moyenne</h2>
<p>{echantillon(c, "à Saint-Renan")}, {recent} % concernent des logements construits depuis 1989, contre {recent_t} % dans l'ensemble des communes que nous suivons. {LIMITE}</p>
<p>Pour un bien dont le permis de construire est postérieur au 1er juillet 1997, ni l'amiante ni le plomb ne sont requis. En revanche, récent ne veut pas dire dispensé : dès que l'installation a quinze ans, les diagnostics <a href="/diagnostics/electricite/">électricité</a> et <a href="/diagnostics/gaz/">gaz</a> font partie du dossier de vente comme de location.</p>
<h2>Plus d'un logement diagnostiqué sur deux chauffé à l'électricité</h2>
<p>L'électricité est l'énergie de chauffage de {k["pelec"]} % des logements diagnostiqués à Saint-Renan, contre {kt["pelec"]} % en moyenne. C'est le profil le plus concerné par le coefficient applicable au 1er janvier 2027 (1,7 au lieu de 1,9). Les DPE en cours restent valables ; <a href="/dpe-2027/">notre simulateur</a> estime la future étiquette. <a href="/diagnostics/dpe/iroise/">Le DPE à Saint-Renan et dans le pays d'Iroise</a>.</p>
<h2>{nb(k["efg"])} DPE classés E, F ou G</h2>
<p>Soit {k["pefg"]} % des DPE enregistrés, moins que dans l'ensemble des communes que nous suivons ({kt["pefg"]} %). Pour une maison dans ce cas, l'<a href="/diagnostics/audit-energetique/iroise/">audit énergétique</a> est obligatoire à la vente. Pour les copropriétés : <a href="/diagnostics/pppt/iroise/">PPPT</a> et <a href="/diagnostics/dtg/iroise/">DTG</a> dans le pays d'Iroise.</p>"""
    faq = [("Ma maison de Saint-Renan date de 2002 : quels diagnostics pour la vendre ?", "Le DPE et l'état des risques, ainsi que les diagnostics électricité et gaz puisque les installations ont plus de quinze ans. Le permis de construire étant postérieur au 1er juillet 1997, ni l'amiante ni le plomb ne sont requis. Nous réalisons aussi l'état parasitaire sur tous les biens."),
           ("Mon DPE de 2023 reste-t-il valable après le 1er janvier 2027 ?", "Oui, il reste valable jusqu'à sa date de fin de validité. Si le logement est chauffé à l'électricité, une attestation de nouvelle étiquette pourra être obtenue auprès de l'ADEME à partir du 1er janvier 2027, sans refaire le diagnostic."),
           ("Intervenez-vous au Conquet, à Ploudalmézeau ou à Plouarzel ?", "Oui, dans tout le pays d'Iroise : " + ", ".join(f'<a href="/secteurs/{slug(n)}/">{n}</a>' for n in autour) + ".")]
    return "", bas, faq

LOCAL = {
 "Lesneven": dict(f=_lesneven, titre="DPE et diagnostic immobilier à Lesneven : agence en centre-ville | Arliane",
    desc=lambda c, k: f"DPE, amiante, plomb, électricité, gaz, audit énergétique : tous vos diagnostics immobiliers à Lesneven. Agence au 15 rue Général de Gaulle. {nb(c['n'])} DPE analysés. Devis gratuit."),
 "Brest": dict(f=_brest, titre="Diagnostiqueur immobilier Brest : DPE, amiante, audit énergétique | Arliane",
    desc=lambda c, k: f"Diagnostiqueur immobilier à Brest : DPE, amiante, loi Carrez, audit énergétique, PPPT et DTG de copropriété. {nb(c['n'])} DPE analysés, {k['pefg']} % classés E, F ou G. Devis gratuit."),
 "Plabennec": dict(f=_plabennec, titre="Diagnostic immobilier Plabennec : DPE, audit énergétique, amiante | Arliane",
    desc=lambda c, k: f"Diagnostic immobilier à Plabennec : DPE, audit énergétique des maisons classées E, F ou G, amiante, électricité, gaz. {nb(c['n'])} DPE analysés, {k['pefg']} % classés E, F ou G. Devis gratuit."),
 "Morlaix": dict(f=_morlaix, devis=True, titre="Diagnostiqueur immobilier Morlaix : DPE, amiante, plomb, audit énergétique | Arliane",
    accroche="Nous réalisons vos diagnostics immobiliers à Morlaix et autour de sa baie : vente d'un appartement ou d'une maison, mise en location, travaux, copropriété. Le rendez-vous se prend par téléphone auprès de notre agence de Lesneven.",
    desc=lambda c, k: f"Diagnostiqueur immobilier à Morlaix : DPE, amiante, plomb, loi Carrez, audit énergétique, PPPT de copropriété. {nb(c['n'])} DPE analysés, {k['pefg']} % classés E, F ou G. Devis gratuit."),
 "Landerneau": dict(f=_landerneau, devis=True, titre="Diagnostiqueur immobilier Landerneau : DPE, amiante, loi Carrez, audit | Arliane",
    desc=lambda c, k: f"Diagnostiqueur immobilier à Landerneau : DPE, amiante, loi Carrez, audit énergétique, PPPT et DPE collectif de copropriété. {nb(c['n'])} DPE analysés. Devis gratuit."),
 "Landivisiau": dict(f=_landivisiau, devis=True, titre="Diagnostic immobilier Landivisiau : DPE, audit énergétique, amiante | Arliane",
    desc=lambda c, k: f"Diagnostic immobilier à Landivisiau : la liste des diagnostics selon votre bien, DPE, audit énergétique, amiante, gaz. {nb(c['n'])} DPE analysés, {k['pefg']} % classés E, F ou G. Devis gratuit."),
 "Saint-Pol-de-Léon": dict(f=_saintpol, devis=True, titre="Diagnostic immobilier Saint-Pol-de-Léon : DPE, audit énergétique, plomb | Arliane",
    accroche="Nous réalisons vos diagnostics immobiliers à Saint-Pol-de-Léon, à Roscoff et dans tout le Haut-Léon, pour les ventes, les mises en location et les copropriétés.",
    desc=lambda c, k: f"Diagnostic immobilier à Saint-Pol-de-Léon : DPE, audit énergétique, plomb, amiante, état parasitaire. {nb(c['n'])} DPE analysés, {k['pefg']} % classés E, F ou G. Devis gratuit."),
 "Saint-Renan": dict(f=_saintrenan, devis=True, titre="Diagnostic immobilier Saint-Renan : DPE, électricité, gaz, audit énergétique | Arliane",
    accroche="Nous réalisons vos diagnostics immobiliers à Saint-Renan et dans le pays d'Iroise, de Ploudalmézeau au Conquet, pour les ventes, les locations et les copropriétés.",
    desc=lambda c, k: f"Diagnostic immobilier à Saint-Renan : DPE, électricité, gaz, audit énergétique, effet du coefficient 2027. {nb(c['n'])} DPE analysés, {k['pelec']} % chauffés à l'électricité. Devis gratuit."),
}

def pages_projets(zd, C, tout, kt):
    etapes = '<div class="atouts"><div><strong>1. Un appel</strong><p>Nous vérifions avec vous les diagnostics réellement nécessaires pour votre bien.</p></div><div><strong>2. Une visite</strong><p>Tous les diagnostics sont réalisés lors d\'un même rendez-vous.</p></div><div><strong>3. Vos rapports</strong><p>Ils vous sont envoyés par e-mail, prêts à être transmis au notaire, à l\'agence ou aux entreprises.</p></div></div>'
    page("/projets/", "Vente, location, travaux : vos diagnostics par projet | Arliane Diagnostic Nord Finistère", "Vous vendez une maison, un appartement, vous louez ou vous préparez des travaux ? La liste des diagnostics immobiliers à prévoir selon votre projet.",
         "Vos diagnostics selon votre projet", f'<p class="chapo">Chaque projet a sa liste de diagnostics. Choisissez le vôtre.</p>{cartes([(f"/projets/{p["slug"]}/", p["nom"], p["intro"].split(". ")[0] + ".") for p in PROJETS])}<p>Vous gérez une copropriété ? Voir nos pages <a href="/diagnostics/pppt/">PPPT</a>, <a href="/diagnostics/dtg/">DTG</a> et <a href="/diagnostics/dpe-collectif/">DPE collectif</a>.</p>',
         crumbs=[("Votre projet", "/projets/")])
    for p in PROJETS:
        body = f"""<p class="chapo">{p['intro']}</p>
{BTN}
<h2>Les diagnostics à prévoir</h2>{ul(p['liste']())}
<p class="note">Liste indicative : nous la confirmons gratuitement pour votre bien. <a href="/quels-diagnostics/">Obtenez votre liste en six questions</a>.</p>
<h2>Dans le Nord-Finistère</h2><p>{p['stat'](tout, kt, "dans le Nord-Finistère")}</p>{barres(tout)}{SRC}
<h2>Comment ça se passe ?</h2>{etapes}
<h2>Par secteur</h2>{cartes([(f"/projets/{p['slug']}/{z[0]}/", z[1], p['nom'] + ' ' + z[3]) for z in ZONES])}
{faq_html(p['faq'])}"""
        page(f"/projets/{p['slug']}/", f"{p['seo']} : la liste complète | Arliane Diagnostic Nord Finistère", f"{p['h1']} dans le Nord-Finistère : liste des diagnostics obligatoires, durées de validité et intervention rapide. Devis gratuit.",
             p["h1"], body, crumbs=[("Votre projet", "/projets/"), (p["nom"], f"/projets/{p['slug']}/")], ld=[faq_ld(p["faq"])])
        for zs, centre, lib, dans, idx in ZONES:
            d = zd[zs]; k = chiffres(d); cs = sorted([C[i] for i in idx if i in C], key=lambda c: -c["n"])
            body = f"""<p class="chapo">{p['intro']}</p>
{BTN}
<h2>Les diagnostics à prévoir</h2>{ul(p['liste']())}
<p class="note">Liste indicative : nous la confirmons gratuitement pour votre bien. <a href="/quels-diagnostics/">Obtenez votre liste en six questions</a>.</p>
<h2>La situation {dans}</h2><p>{p['stat'](d, k, dans)}</p>{tuiles(d, k)}{barres(d)}{SRC}
<h2>Comment ça se passe ?</h2>{etapes}
<h2>Nos prestations {dans}</h2>{cartes([(f"/diagnostics/{s}/{zs}/", DIAG[s]["nom"] + " – " + centre, DIAG[s]["titre"] + " " + dans) for s in SERVICES_ZONE])}
<h2>Communes desservies</h2><p>{liens_communes(cs)}. <a href="{zpath(zs)}">Voir le secteur</a>.</p>
<p>{e(p['nom'])} dans les autres secteurs : {autres_zones(f"/projets/{p['slug']}/", zs)}.</p>
{faq_html(p['faq'])}"""
            page(f"/projets/{p['slug']}/{zs}/", f"{p['seo']} {centre} : la liste pour votre bien | Arliane", f"{p['h1']} {dans} : liste des diagnostics obligatoires, chiffres locaux, devis gratuit.",
                 f"{p['h1']} {dans}", body, crumbs=[("Votre projet", "/projets/"), (p["nom"], f"/projets/{p['slug']}/"), (centre, f"/projets/{p['slug']}/{zs}/")], ld=[faq_ld(p["faq"])])

def build():
    B.ZONES_PIED[:] = [(zpath(z[0]), z[1]) for z in ZONES]
    C = charger()
    B.COMMUNES_LD[:] = [c["nom"] for c in C.values()]
    B.extra_diag = extra_diag
    B.build()
    shutil.copy(B.SRC + "/quels.js", OUT + "/assets/quels.js")
    shutil.copytree(B.SRC + "/photos", OUT + "/assets/photos", dirs_exist_ok=True)
    shutil.rmtree(OUT + "/secteurs", ignore_errors=True)
    B.pages[:] = [p for p in B.pages if not p[0].startswith("/secteurs/")]
    zd = {z[0]: somme([C[i] for i in z[4] if i in C]) for z in ZONES}
    tout = somme(list(C.values())); kt = chiffres(tout); tout["nbc"] = len(C)

    # ---------------- communes
    for c in C.values():
        z = c["zone"]; k = chiffres(c); nom = c["nom"]; ou = a_la(nom); m = MAIN.get(nom)
        intro = m["accroche"] if m else f"Notre agence de Lesneven réalise l'ensemble de vos diagnostics immobiliers {ou} : vente, location, travaux, copropriété. Nous nous déplaçons chez vous sous quelques jours."
        voisines = [C[i] for i in z[4] if i in C and i != c["i"]]
        avert = '<p class="note">Le nombre de DPE enregistrés est faible : les pourcentages sont à lire avec prudence.</p>' if c["n"] < 80 else ""
        faq = [(f"Quels diagnostics faut-il pour vendre {ou} ?", "Le DPE et l'état des risques dans tous les cas, auxquels s'ajoutent selon le bien l'amiante, le plomb, l'électricité, le gaz, le mesurage loi Carrez et l'audit énergétique. <a href=\"/quels-diagnostics/\">Obtenez la liste pour votre bien</a>."),
               (f"Sous quel délai intervenez-vous {ou} ?", f"Nous proposons en général un rendez-vous sous quelques jours. Appelez-nous au {TEL}.")]
        kz = chiffres(zd[z[0]]); loc = LOCAL.get(nom)
        if loc and loc.get("accroche"): intro = loc["accroche"]
        devis_btn = devis_p(f"Demander un devis pour {nom}", nom) if loc and loc.get("devis") else ""
        haut, bas, faq_loc = loc["f"](c, k, kt, tout) if loc else ("", "", [])
        faq = faq_loc + faq
        arts = articles_pour(k)
        body = f"""<p class="chapo">{intro}</p>
{BTN}
{devis_btn}{haut}
<h2>Le DPE {ou} en chiffres</h2>
{tuiles(c, k)}{barres(c)}{avert}{SRC}
<h2>Ce que ces chiffres disent du bâti {de_la(nom)}</h2>
{("<p>" + m["bati"] + "</p>") if m else ""}{analyse(ou, k)}
{bas}
<h2>Âge du bâti et énergies de chauffage {ou}</h2>
{table_periodes(c)}{phrase_energies(c, ou)}
<h2>{e(nom)} comparé à son secteur et au Nord-Finistère</h2>
{table_compar(nom, k, z[2], kz, kt)}{phrase_compar(nom, k, kt)}
<p class="note">Même source et même date d'extraction que ci-dessus. <a href="/observatoire-dpe-nord-finistere/">Voir l'observatoire DPE du Nord-Finistère</a>.</p>
<h2>Tous nos diagnostics {ou}</h2>{cartes_diags()}
{secteur_local(z)}
<h2>Copropriétés et professionnels</h2><p>Syndics, conseils syndicaux, agences et notaires {de_la(nom)} : nous réalisons le <a href="/diagnostics/pppt/">projet de plan pluriannuel de travaux (PPPT)</a>, le <a href="/diagnostics/dtg/">diagnostic technique global (DTG)</a>, le <a href="/diagnostics/dpe-collectif/">DPE collectif</a> et les <a href="/diagnostics/amiante/">repérages amiante avant travaux</a>. <a href="/professionnels/">Voir notre accompagnement des professionnels</a>.</p>
<h2>Communes voisines</h2><p>{liens_communes(voisines)}. <a href="{zpath(z[0])}">Tout le secteur : {e(z[2])}</a>.</p>
<h2>À lire pour votre projet {ou}</h2>{liens_art(arts)}
{faq_html(faq)}"""
        page(cpath(c), loc["titre"] if loc else f"Diagnostic immobilier {nom} : DPE, audit, amiante | Arliane", loc["desc"](c, k) if loc else f"Diagnostics immobiliers {ou} : DPE, audit énergétique, amiante, plomb, PPPT. {nb(c['n'])} DPE analysés, {k['pefg']} % classés E, F ou G. Devis gratuit.",
             f"Diagnostic immobilier {ou}", body, crumbs=[("Secteurs", "/secteurs/"), (z[1], zpath(z[0])), (nom, cpath(c))], ld=[faq_ld(faq)])

    # ---------------- secteurs
    for zs, centre, lib, dans, idx in ZONES:
        d = zd[zs]; k = chiffres(d); cs = sorted([C[i] for i in idx if i in C], key=lambda c: -c["n"])
        lignes = "".join(f'<tr><th scope="row"><a href="{cpath(c)}">{e(c["nom"])}</a></th><td>{nb(c["n"])}</td><td>{chiffres(c)["pefg"]} %</td><td>{chiffres(c)["pmaison"]} %</td><td>{chiffres(c)["pelec"]} %</td></tr>' for c in cs)
        body = f"""<p class="chapo">Notre agence de Lesneven réalise vos diagnostics immobiliers {dans} : {", ".join(c["nom"] for c in cs)}.</p>
{BTN}
<h2>Le DPE du secteur en chiffres</h2>{tuiles(d, k)}{barres(d)}{SRC}
<h2>Ce que ces chiffres disent du bâti</h2>{analyse("dans ce secteur", k)}
<h2>Commune par commune</h2><div class="defile"><table><thead><tr><th scope="col">Commune</th><th scope="col">DPE enregistrés</th><th scope="col">Classés E, F ou G</th><th scope="col">Maisons</th><th scope="col">Chauffage électrique</th></tr></thead><tbody>{lignes}</tbody></table></div>
<h2>Nos prestations dans le secteur</h2>{cartes([(f'/diagnostics/{s}/{zs}/', DIAG[s]['nom'] + ' – ' + centre, DIAG[s]['titre'] + ' ' + dans) for s in SERVICES_ZONE])}
<h2>Selon votre projet</h2>{cartes([(f"/projets/{p['slug']}/{zs}/", p['nom'], p['h1'] + ' ' + dans) for p in PROJETS])}
<h2>Tous nos diagnostics</h2>{cartes_diags()}"""
        page(zpath(zs), f"Diagnostic immobilier {centre} et alentours | Arliane", f"Diagnostics immobiliers {dans} : DPE, audit énergétique, amiante, PPPT, DTG. {nb(d['n'])} DPE analysés, chiffres commune par commune. Devis gratuit.",
             f"Diagnostic immobilier {dans}", body, crumbs=[("Secteurs", "/secteurs/"), (centre, zpath(zs))])

        # ---------------- service × secteur
        for s in SERVICES_ZONE:
            D = DIAG[s]
            if s == "dpe":
                spec = f"""<h2>Le DPE {dans} en chiffres</h2>{tuiles(d, k)}{barres(d)}{SRC}
<p>Sur les {nb(d['n'])} DPE enregistrés dans le secteur, {k['pefg']} % sont classés E, F ou G et {k['pelec']} % concernent des logements chauffés à l'électricité. Ces derniers sont directement concernés par le nouveau coefficient applicable au 1er janvier 2027 : <a href="/dpe-2027/">testez votre DPE avec notre simulateur</a>.</p>"""
            elif s == "audit-energetique":
                spec = f"""<h2>Combien de logements concernés {dans} ?</h2>
<div class="chiffres"><div><b>{nb(k['efg'])}</b><span>DPE classés E, F ou G</span></div><div><b>{k['pefg']} %</b><span>des DPE du secteur</span></div><div><b>{k['pmaison']} %</b><span>de maisons</span></div><div><b>{k['pfioul']} %</b><span>chauffés au fioul</span></div></div>{barres(d)}{SRC}
<p>L'audit énergétique est obligatoire pour vendre une maison ou un immeuble en monopropriété classé E, F ou G. Avec {k['pmaison']} % de maisons parmi les logements diagnostiqués, le secteur est {"très largement" if k['pmaison'] >= 70 else "directement"} concerné.</p>"""
            else:
                spec = f"""<h2>Les copropriétés {dans}</h2>
<div class="chiffres"><div><b>{nb(d['appart'])}</b><span>DPE d'appartements</span></div><div><b>{k['pappart']} %</b><span>des logements diagnostiqués</span></div><div><b>{k['pav75']} %</b><span>construits avant 1975</span></div><div><b>{k['pefg']} %</b><span>classés E, F ou G</span></div></div>{SRC}
<p>{"Le secteur compte un parc collectif important, avec de nombreuses copropriétés anciennes à rénover." if k['pappart'] >= 40 else "Le secteur compte surtout de petites copropriétés de centre-bourg, souvent gérées par un syndic bénévole, pour lesquelles l'obligation est encore mal connue."} Toutes les copropriétés de plus de quinze ans sont aujourd'hui concernées par le projet de plan pluriannuel de travaux.</p>"""
            faq = D["faq"][:2]
            body = f"""<p class="chapo">{D['intro']}</p>
{BTN}
{spec}
<h2>Quand est-il obligatoire ?</h2>{ul(D['quand'])}
<div class="fiche"><div><strong>Durée de validité</strong><p>{D['validite']}</p></div><div><strong>En savoir plus</strong><p><a href="/diagnostics/{s}/">Notre page complète : {e(D['titre'])}</a></p></div></div>
<h2>Communes desservies</h2><p>{liens_communes(cs)}. <a href="{zpath(zs)}">Tout le secteur : {e(lib)}</a>.</p>
<h2>Autres prestations {dans}</h2>{cartes([(f"/diagnostics/{x}/{zs}/", DIAG[x]["nom"] + " – " + centre, DIAG[x]["titre"] + " " + dans) for x in SERVICES_ZONE if x != s] + [(f"/projets/{p['slug']}/{zs}/", p["nom"], p["h1"] + " " + dans) for p in projets_de(s)])}
<p>{e(D['nom'])} dans les autres secteurs : {autres_zones(f"/diagnostics/{s}/", zs)}.</p>
{("<h2>À lire sur ce sujet</h2>" + liens_art(ART_DIAG[s])) if ART_DIAG.get(s) else ""}
{faq_html(faq)}"""
            page(f"/diagnostics/{s}/{zs}/", TITRES_ZONE[s].format(centre=centre), f"{D['titre']} {dans} : obligations, chiffres locaux, intervention rapide. Devis gratuit.",
                 f"{D['titre']} {dans}", body, crumbs=[("Diagnostics", "/diagnostics/"), (D["nom"], f"/diagnostics/{s}/"), (centre, f"/diagnostics/{s}/{zs}/")],
                 ld=[faq_ld(faq), {"@context": "https://schema.org", "@type": "Service", "name": f"{D['titre']} {dans}", "serviceType": D["titre"], "provider": {"@id": BASE + "/#agence"}, "areaServed": [{"@type": "City", "name": x["nom"]} for x in cs], "url": BASE + f"/diagnostics/{s}/{zs}/"}])

    # ---------------- hub secteurs : page pilier Nord-Finistère
    blocs = "".join(f'<h3><a href="{zpath(z[0])}">{e(z[2])}</a></h3><p>{liens_communes([C[i] for i in z[4] if i in C])}.</p>' for z in ZONES)
    ligz = "".join(f'<tr><th scope="row"><a href="{zpath(z[0])}">{e(z[2])}</a></th><td>{len([i for i in z[4] if i in C])}</td><td>{nb(zd[z[0]]["n"])}</td><td>{chiffres(zd[z[0]])["pefg"]} %</td><td>{chiffres(zd[z[0]])["pmaison"]} %</td><td>{chiffres(zd[z[0]])["pelec"]} %</td></tr>' for z in ZONES)
    fortes = [c for n in ["Brest", "Morlaix", "Landerneau", "Landivisiau", "Lesneven", "Saint-Pol-de-Léon", "Saint-Renan", "Plabennec"] for c in C.values() if c["nom"] == n]
    prest = "".join(f'<p><strong>{e(DIAG[sv]["titre"])}</strong> : ' + ", ".join(f'<a href="/diagnostics/{sv}/{z[0]}/">{e(z[1])}</a>' for z in ZONES) + f'. <a href="/diagnostics/{sv}/">Tout savoir</a>.</p>' for sv in SERVICES_ZONE)
    faq = [("Dans quelles communes du Nord-Finistère intervenez-vous ?", f"Dans {len(C)} communes réparties en huit secteurs, de la pointe Saint-Mathieu à la baie de Morlaix. Si votre commune ne figure pas dans la liste, appelez-nous au {TEL} : nous vous dirons si nous pouvons intervenir."),
           ("Où se trouve votre cabinet ?", f"Notre agence est installée au {B.RUE}, {B.CP} {B.VILLE}. Elle est ouverte du lundi au vendredi, de 9h à 12h et de 14h à 18h. Les diagnostiqueurs se déplacent chez vous dans tout le Finistère Nord."),
           ("Réalisez-vous aussi les diagnostics de copropriété ?", "Oui : le <a href=\"/diagnostics/pppt/\">projet de plan pluriannuel de travaux (PPPT)</a>, le <a href=\"/diagnostics/dtg/\">diagnostic technique global (DTG)</a> et le <a href=\"/diagnostics/dpe-collectif/\">DPE collectif</a>, en partenariat avec un bureau d'études structure et thermique."),
           ("Comment obtenir un devis ?", f"Par téléphone au {TEL}, ou par e-mail en indiquant la commune, le type de bien et votre projet. <a href=\"/devis/\">Voir les informations utiles pour un devis</a>.")]
    page("/secteurs/", "Diagnostiqueur immobilier Nord-Finistère : 8 secteurs, " + str(len(C)) + " communes | Arliane",
         f"Diagnostic immobilier dans le Finistère Nord : DPE, audit énergétique, amiante, plomb, DTG, PPPT. Cabinet à Lesneven, diagnostiqueurs certifiés, {len(C)} communes de Brest à Morlaix. Devis gratuit.",
         "Diagnostic immobilier dans le Nord-Finistère", f"""<p class="chapo">{e(B.NOM)} est un cabinet de diagnostic immobilier installé à Lesneven. Nos diagnostiqueurs, certifiés par Abcidia Certification, interviennent dans tout le Finistère Nord, de la pointe Saint-Mathieu à la baie de Morlaix : {len(C)} communes réparties en huit secteurs.</p>
{BTN}
{devis_p("Demander un devis par e-mail", "Nord-Finistère")}
<h2>Huit secteurs d'intervention</h2>
{cartes([(zpath(z[0]), z[2], f"{len([i for i in z[4] if i in C])} communes, {nb(zd[z[0]]['n'])} DPE analysés") for z in ZONES])}
<h2>Le Nord-Finistère en chiffres, secteur par secteur</h2>
<p>Nous avons analysé {nb(tout['n'])} DPE enregistrés dans ces {len(C)} communes : {kt['pefg']} % sont classés E, F ou G et {kt['pelec']} % concernent des logements chauffés à l'électricité.</p>
<div class="defile"><table><thead><tr><th scope="col">Secteur</th><th scope="col">Communes</th><th scope="col">DPE enregistrés</th><th scope="col">Classés E, F ou G</th><th scope="col">Maisons</th><th scope="col">Chauffage électrique</th></tr></thead><tbody>{ligz}</tbody></table></div>
{SRC}
<p><a href="/observatoire-dpe-nord-finistere/">Consulter l'observatoire DPE du Nord-Finistère, commune par commune</a>.</p>
<h2>Les villes principales</h2>
{cartes([(cpath(c), c["nom"], f"{nb(c['n'])} DPE analysés, {chiffres(c)['pefg']} % classés E, F ou G") for c in fortes])}
<h2>Nos prestations dans chaque secteur</h2>
{prest}
<p>Amiante, plomb, électricité, gaz, état parasitaire, mesurage, état des risques : <a href="/diagnostics/">voir tous nos diagnostics</a>, ou <a href="/quels-diagnostics/">obtenez la liste pour votre bien en six questions</a>.</p>
<h2>Toutes les communes desservies</h2>
{blocs}
<p>Votre commune n'apparaît pas ? Appelez-nous au <a href="tel:{TEL_LINK}">{TEL}</a>.</p>
<h2>Un cabinet local, une équipe certifiée</h2>
<p>Notre agence se trouve au {B.RUE}, à {B.VILLE}. L'équipe réunit des diagnostiqueurs certifiés par Abcidia Certification et un accueil à l'agence, du lundi au vendredi. <a href="/agence/">Découvrir l'agence et l'équipe</a> · <a href="/professionnels/">Agences, notaires et syndics</a> · <a href="/contact/">Contact et itinéraire</a>.</p>
{faq_html(faq)}""", crumbs=[("Secteurs", "/secteurs/")], full=True,
         ld=[faq_ld(faq), {"@context": "https://schema.org", "@type": "ItemList", "name": "Secteurs d'intervention dans le Nord-Finistère", "itemListElement": [
             {"@type": "ListItem", "position": n + 1, "name": z[2], "url": BASE + zpath(z[0])} for n, z in enumerate(ZONES)]}])

    # ---------------- observatoire
    cs = sorted(C.values(), key=lambda c: -c["n"])
    gros = [c for c in cs if c["n"] >= 150]
    top_efg = sorted(gros, key=lambda c: -chiffres(c)["pefg"])[:5]; top_elec = sorted(gros, key=lambda c: -chiffres(c)["pelec"])[:5]; top_anc = sorted(gros, key=lambda c: -chiffres(c)["pav48"])[:5]
    lig = "".join(f'<tr><th scope="row"><a href="{cpath(c)}">{e(c["nom"])}</a></th><td>{nb(c["n"])}</td><td>{pct(c["et"][0] + c["et"][1], c["n"])} %</td><td>{pct(c["et"][2] + c["et"][3], c["n"])} %</td><td>{pct(c["et"][4], c["n"])} %</td><td>{chiffres(c)["pfg"]} %</td><td>{chiffres(c)["pelec"]} %</td><td>{chiffres(c)["pav48"]} %</td></tr>' for c in cs)
    ligz = "".join(f'<tr><th scope="row"><a href="{zpath(z[0])}">{e(z[2])}</a></th><td>{nb(zd[z[0]]["n"])}</td><td>{chiffres(zd[z[0]])["pefg"]} %</td><td>{chiffres(zd[z[0]])["pfg"]} %</td><td>{chiffres(zd[z[0]])["pmaison"]} %</td><td>{chiffres(zd[z[0]])["pelec"]} %</td></tr>' for z in ZONES)
    def top(l, cle): return ul([f'<a href="{cpath(c)}">{e(c["nom"])}</a> : {chiffres(c)[cle]} %' for c in l])
    body = f"""<p class="chapo">Combien de logements classés E, F ou G dans votre commune ? Quelle part de chauffage électrique ? Nous avons analysé {nb(tout['n'])} DPE enregistrés dans {len(C)} communes du Nord-Finistère.</p>
<h2>L'essentiel</h2>{tuiles(tout, kt)}{barres(tout)}{SRC}
<h2>Par secteur</h2><div class="defile"><table><thead><tr><th scope="col">Secteur</th><th scope="col">DPE</th><th scope="col">E, F ou G</th><th scope="col">F ou G</th><th scope="col">Maisons</th><th scope="col">Chauffage électrique</th></tr></thead><tbody>{ligz}</tbody></table></div>
<h2>Les communes qui comptent le plus de logements énergivores</h2><p>Part des DPE classés E, F ou G, parmi les communes comptant au moins 150 DPE :</p>{top(top_efg, 'pefg')}
<h2>Les communes les plus chauffées à l'électricité</h2><p>Ce sont celles où le <a href="/dpe-2027/">nouveau coefficient du 1er janvier 2027</a> aura le plus d'effet :</p>{top(top_elec, 'pelec')}
<h2>Les communes au bâti le plus ancien</h2><p>Part des logements diagnostiqués construits avant 1948 :</p>{top(top_anc, 'pav48')}
<h2>Toutes les communes</h2><div class="defile"><table><thead><tr><th scope="col">Commune</th><th scope="col">DPE</th><th scope="col">A ou B</th><th scope="col">C ou D</th><th scope="col">E</th><th scope="col">F ou G</th><th scope="col">Chauffage électrique</th><th scope="col">Avant 1948</th></tr></thead><tbody>{lig}</tbody></table></div>
<h2>Réutiliser ces chiffres</h2><p>Ces données sont issues de la base publique de l'ADEME. Vous pouvez les reprendre librement en citant « Observatoire DPE du Nord-Finistère – Arliane Diagnostic Nord Finistère ».</p>"""
    page("/observatoire-dpe-nord-finistere/", "Observatoire DPE du Nord-Finistère : chiffres par commune | Arliane", f"{nb(tout['n'])} DPE analysés dans {len(C)} communes du Nord-Finistère : étiquettes, passoires thermiques, chauffage électrique, bâti ancien, commune par commune.",
         "Observatoire DPE du Nord-Finistère", body, crumbs=[("Observatoire DPE", "/observatoire-dpe-nord-finistere/")],
         ld=[{"@context": "https://schema.org", "@type": "Dataset", "name": "Observatoire DPE du Nord-Finistère", "description": f"Répartition des étiquettes DPE, du mode de chauffage et de la période de construction dans {len(C)} communes du Nord-Finistère.", "url": BASE + "/observatoire-dpe-nord-finistere/", "creator": {"@id": BASE + "/#agence"}, "isBasedOn": "https://data.ademe.fr/datasets/dpe03existant", "spatialCoverage": "Nord-Finistère, France", "dateModified": "2026-11-17", "license": "https://www.etalab.gouv.fr/licence-ouverte-open-licence"}])

    pages_projets(zd, C, tout, kt)

    # ---------------- questionnaire
    faq = [("Cette liste est-elle officielle ?", "Elle est indicative : elle repose sur vos réponses. Nous la confirmons gratuitement avec vous par téléphone avant toute intervention."),
           ("Et la mérule ou les termites ?", "Nous réalisons un <a href=\"/diagnostics/etat-parasitaire/\">état parasitaire</a> sur tous les biens : il recherche la mérule et les insectes du bois. Notre secteur n'est pas concerné par les termites.")]
    page("/quels-diagnostics/", "Quels diagnostics pour mon bien ? Liste en 1 minute | Arliane Diagnostic Nord Finistère", "Vente, location, travaux ou copropriété : répondez à six questions et obtenez la liste des diagnostics immobiliers obligatoires pour votre bien.",
         "Quels diagnostics immobiliers pour mon bien ?", f"""<p class="chapo">Répondez à six questions : nous vous indiquons les diagnostics à faire réaliser pour votre projet.</p>
{QUESTIONNAIRE}
<h2>Vous préférez un tableau ?</h2><p>Notre page <a href="/vente-location/">vente ou location</a> récapitule tous les diagnostics obligatoires et leurs durées de validité.</p>
{faq_html(faq)}""", crumbs=[("Quels diagnostics ?", "/quels-diagnostics/")], ld=[faq_ld(faq)])

    # ---------------- actualités
    page("/actualites/", "Actualités du diagnostic immobilier dans le Finistère | Arliane Diagnostic Nord Finistère", "DPE 2027, passoires thermiques, audit énergétique, PPPT, radon, mérule : l'actualité du diagnostic immobilier expliquée pour le Nord-Finistère.",
         "Actualités du diagnostic immobilier", f'<p class="chapo">La réglementation évolue vite. Nous l\'expliquons simplement, avec les chiffres du Nord-Finistère.</p>{cartes([("/actualites/" + a["slug"] + "/", a["titre"], a["desc"]) for a in ARTICLES])}',
         crumbs=[("Actualités", "/actualites/")])
    for a in ARTICLES:
        autres = [x for x in ARTICLES if x is not a]
        sv = ART_SERVICE.get(a["slug"])
        if sv: pres = f'<h2>{e(DIAG[sv]["nom"])} près de chez vous</h2><p>' + ", ".join(f'<a href="/diagnostics/{sv}/{z[0]}/">{e(DIAG[sv]["nom"])} {e(z[1])}</a>' for z in ZONES) + f'. <a href="/diagnostics/{sv}/">Notre page {e(DIAG[sv]["titre"])}</a>.</p>'
        else: pres = "<h2>Nos secteurs d'intervention</h2><p>" + ", ".join(f'<a href="{zpath(z[0])}">{e(z[2])}</a>' for z in ZONES) + ".</p>"
        pres += f'<p>Diagnostic immobilier dans les villes principales : {liens_princ()}.</p>'
        page(f"/actualites/{a['slug']}/", a["titre"] + " | Arliane", a["desc"], a["titre"],
             a["corps"](kt) + pres + "<h2>À lire aussi</h2>" + cartes([("/actualites/" + x["slug"] + "/", x["titre"], x["desc"]) for x in autres]),
             crumbs=[("Actualités", "/actualites/"), (a["titre"], f"/actualites/{a['slug']}/")],
             ld=[{"@context": "https://schema.org", "@type": "Article", "headline": a["titre"], "description": a["desc"], "datePublished": a["date"], "dateModified": a["date"], "image": BASE + "/assets/photos/agence-arliane-lesneven.jpg", "author": {"@id": BASE + "/#agence"}, "publisher": {"@id": BASE + "/#agence"}, "mainEntityOfPage": BASE + f"/actualites/{a['slug']}/"}])

    # ---------------- agence
    PH_EQ = """<figure class="photo"><picture><source type="image/webp" srcset="/assets/photos/equipe-arliane-lesneven-640.webp 640w, /assets/photos/equipe-arliane-lesneven.webp 1200w" sizes="(max-width:700px) 100vw, 900px"><img src="/assets/photos/equipe-arliane-lesneven.jpg" width="1200" height="800" loading="lazy" alt="L'équipe de l'agence Arliane Diagnostic Nord Finistère, à Lesneven"></picture><figcaption>L'équipe de l'agence de Lesneven</figcaption></figure>"""
    PH_AG = """<figure class="photo etroite"><picture><source type="image/webp" srcset="/assets/photos/agence-arliane-lesneven.webp"><img src="/assets/photos/agence-arliane-lesneven.jpg" width="614" height="490" loading="lazy" alt="Façade de l'agence Arliane Diagnostic Nord Finistère, 15 rue Général de Gaulle à Lesneven"></picture><figcaption>Notre agence, 15 rue Général de Gaulle à Lesneven</figcaption></figure>"""
    PH_AG0 = PH_AG.replace('loading="lazy" ', 'fetchpriority="high" ')
    body = f"""<p class="chapo">« Fondée par la famille, portée par la confiance, dédiée à votre tranquillité » : c'est la devise inscrite sur notre vitrine, au cœur de Lesneven.</p>
{PH_EQ}
<h2>Une équipe locale à votre écoute</h2>
<p>Notre équipe réunit des diagnostiqueurs certifiés et un accueil à l'agence. Nous réalisons l'ensemble des diagnostics immobiliers, pour les particuliers comme pour les professionnels, dans tout le Nord-Finistère.</p>
<p><a class="btn" href="tel:{TEL_LINK}">📞 {TEL}</a> <a class="btn clair" href="/devis/">Demander un devis gratuit</a></p>
{B.AVIS}
<h2>Une agence en centre-ville de Lesneven</h2>
{PH_AG}
<p>Nous vous accueillons au {B.RUE}, {B.CP} {B.VILLE}, du lundi au vendredi, de 9h à 12h et de 14h à 18h. <a href="/contact/">Coordonnées et itinéraire</a>.</p>
<h2>Ce que nous faisons</h2>
{cartes([(f'/diagnostics/{d["slug"]}/', d["nom"], d["intro"].split(". ")[0].rstrip(".") + ".") for d in DIAGS])}
<h2>Où nous intervenons</h2>
{cartes([(zpath(z[0]), z[2], f"{len([i for i in z[4] if i in C])} communes desservies") for z in ZONES])}"""
    page("/agence/", f"Notre agence de Lesneven et notre équipe | {B.NOM}", f"Découvrez l'équipe et l'agence {B.NOM} à Lesneven : diagnostiqueurs immobiliers certifiés, accueil en centre-ville, interventions dans tout le Nord-Finistère.",
         "Notre agence de Lesneven et son équipe", body, crumbs=[("Notre agence", "/agence/")], full=True)

    # ---------------- accueil
    faq = [("Quels diagnostics sont obligatoires pour vendre ?", "Cela dépend de l'âge du bien, de son type et de sa localisation. Le DPE et l'état des risques sont toujours requis ; s'y ajoutent selon les cas l'amiante, le plomb, l'électricité, le gaz, l'état parasitaire, le mesurage loi Carrez et l'audit énergétique. <a href=\"/quels-diagnostics/\">Obtenez la liste pour votre bien</a>."),
           ("Sous quel délai pouvez-vous intervenir ?", "Nous proposons en général un rendez-vous sous quelques jours. Les rapports vous sont transmis par e-mail."),
           ("Réalisez-vous les audits énergétiques, les DTG et les PPPT ?", "Oui. Nous réalisons l'<a href=\"/diagnostics/audit-energetique/\">audit énergétique réglementaire</a> et, pour les copropriétés, le <a href=\"/diagnostics/pppt/\">PPPT</a>, le <a href=\"/diagnostics/dtg/\">DTG</a> et le <a href=\"/diagnostics/dpe-collectif/\">DPE collectif</a>."),
           ("Dans quelles communes intervenez-vous ?", f"Dans tout le Nord-Finistère : Lesneven, Brest, Landerneau, Landivisiau, Plabennec, Lannilis, Saint-Pol-de-Léon, Saint-Renan, Morlaix et les communes voisines. <a href=\"/secteurs/\">Voir les {len(C)} communes</a>."),
           ("Intervenez-vous pour les professionnels ?", "Oui : agences immobilières, notaires, syndics de copropriété, bailleurs et entreprises de travaux. <a href=\"/professionnels/\">Voir notre accompagnement des professionnels</a>.")]
    body = f"""<p class="chapo">Vous vendez, vous louez, vous préparez des travaux ou vous gérez une copropriété ? Notre agence de Lesneven et ses diagnostiqueurs immobiliers certifiés réalisent tous vos diagnostics dans le Nord-Finistère, de <a href="/secteurs/lesneven/">Lesneven</a> à <a href="/secteurs/brest/">Brest</a> en passant par <a href="/secteurs/plabennec/">Plabennec</a> : DPE, audit énergétique, amiante, plomb, électricité, gaz, DTG et PPPT.</p>
<p><a class="btn" href="tel:{TEL_LINK}">📞 {TEL}</a> <a class="btn clair" href="/devis/">Demander un devis gratuit</a></p>
{B.AVIS}
{PH_AG0}
<h2>Quels diagnostics pour votre bien ?</h2><p>Répondez à six questions, nous vous donnons la liste.</p>
{QUESTIONNAIRE}
<h2>Votre projet</h2>
{cartes([(f"/projets/{p['slug']}/", p['nom'], p['h1']) for p in PROJETS])}
<div class="bandeau"><strong>Nouveau : votre DPE change-t-il de lettre au 1er janvier 2027 ?</strong> Saisissez votre numéro ADEME et découvrez votre future étiquette. <a href="/dpe-2027/">Essayer le simulateur gratuit</a></div>
<h2>Tous vos diagnostics, un seul interlocuteur</h2>
{cartes([(f'/diagnostics/{d["slug"]}/', d["nom"], d["intro"].split(". ")[0].rstrip(".") + ".") for d in DIAGS])}
<h2>Pourquoi nous confier vos diagnostics ?</h2>
<div class="atouts">
<div><strong>Une agence locale</strong><p>Une équipe basée à Lesneven, qui connaît le bâti du Nord-Finistère et se déplace chez vous rapidement.</p></div>
<div><strong>Des diagnostiqueurs certifiés</strong><p>Chaque diagnostic est réalisé par un opérateur certifié par Abcidia Certification et assuré, comme l'exige la réglementation.</p></div>
<div><strong>Du DPE à la copropriété</strong><p>Particuliers, professionnels, syndics : un seul interlocuteur, du simple DPE à l'audit énergétique, au DTG et au PPPT.</p></div>
<div><strong>La force d'un réseau</strong><p>Membre du réseau national Arliane Diagnostic Immobilier, spécialiste du diagnostic depuis 2007.</p></div>
</div>
{PH_EQ}
<p><a href="/agence/">Découvrir notre agence et notre équipe</a></p>
<h2>Le Nord-Finistère en chiffres</h2>
<p>Nous avons analysé {nb(tout['n'])} DPE enregistrés dans {len(C)} communes : {kt['pefg']} % sont classés E, F ou G et {kt['pelec']} % concernent des logements chauffés à l'électricité. <a href="/observatoire-dpe-nord-finistere/">Consulter l'observatoire DPE du Nord-Finistère</a>.</p>
<h2>Nous intervenons près de chez vous</h2>
{cartes([(zpath(z[0]), z[2], f"{len([i for i in z[4] if i in C])} communes desservies") for z in ZONES])}
<p class="communes">{liens_communes(sorted(C.values(), key=lambda c: c["slug"]))}</p>
<h2>L'actualité du diagnostic</h2>{cartes([("/actualites/" + a["slug"] + "/", a["titre"], a["desc"]) for a in ARTICLES])}
{faq_html(faq)}"""
    page("/", "Diagnostic immobilier Lesneven, Brest, Nord-Finistère | Arliane", "Diagnostiqueur immobilier à Lesneven, Brest, Plabennec et dans tout le Nord-Finistère : DPE, audit énergétique, amiante, plomb, électricité, gaz, DTG, PPPT. Devis gratuit, rendez-vous rapide.",
         "Diagnostic immobilier à Lesneven et dans le Nord-Finistère", body, full=True,
         ld=[faq_ld(faq), {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": B.NOM, "alternateName": B.RAISON, "inLanguage": "fr-FR", "publisher": {"@id": BASE + "/#agence"}}])
    return B.finalize()

if __name__ == "__main__":
    print(len(build()), "pages")
