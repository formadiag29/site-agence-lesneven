(function(){
  var f = document.getElementById("qd"), out = document.getElementById("qd-res");
  if (!f || !out) return;
  function v(id){ return document.getElementById("qd-" + id).value; }
  var L = {dpe:["DPE","/diagnostics/dpe/"], erp:["État des risques (ERP)","/diagnostics/erp/"], amiante:["Diagnostic amiante","/diagnostics/amiante/"],
    plomb:["Diagnostic plomb (CREP)","/diagnostics/plomb/"], elec:["Diagnostic électricité","/diagnostics/electricite/"], gaz:["Diagnostic gaz","/diagnostics/gaz/"],
    carrez:["Mesurage loi Carrez","/diagnostics/loi-carrez-boutin/"], boutin:["Surface habitable (loi Boutin)","/diagnostics/loi-carrez-boutin/"],
    audit:["Audit énergétique","/diagnostics/audit-energetique/"], termites:["État termites ou état parasitaire","/diagnostics/termites/"],
    pppt:["Projet de plan pluriannuel de travaux (PPPT)","/diagnostics/pppt/"], dpecol:["DPE collectif","/diagnostics/dpe-collectif/"], dtg:["Diagnostic technique global (DTG)","/diagnostics/dtg/"]};
  function li(k, note){ return '<li><a href="' + L[k][1] + '">' + L[k][0] + '</a>' + (note ? ' <span>' + note + '</span>' : '') + '</li>'; }
  function calc(){
    var p = v("projet"), t = v("type"), a = v("annee"), el = v("elec"), g = v("gaz"), c = v("classe");
    var ob = [], av = [];
    var ancien = a !== "apres", tresAncien = a === "av1949";
    if (p === "vente" || p === "location"){
      ob.push(li("dpe")); ob.push(li("erp"));
      if (p === "vente"){
        if (ancien) ob.push(li("amiante", "permis de construire antérieur au 1er juillet 1997"));
        if (t === "appartement") ob.push(li("carrez", "lot de copropriété"));
        if (t !== "appartement"){
          if (c === "efg") ob.push(li("audit", "maison ou immeuble classé E, F ou G"));
          else if (c === "inconnu") av.push(li("audit", "obligatoire si le DPE classe le bien en E, F ou G"));
        }
        av.push(li("termites", "selon la commune : nous vérifions pour vous"));
      } else {
        ob.push(li("boutin", "à mentionner dans le bail"));
        if (ancien && t === "appartement") ob.push(li("amiante", "dossier amiante des parties privatives, à tenir à disposition du locataire"));
      }
      if (tresAncien) ob.push(li("plomb", "logement construit avant 1949"));
      if (el === "oui") ob.push(li("elec", "installation de plus de 15 ans")); else if (el === "nsp") av.push(li("elec", "obligatoire si l'installation a plus de 15 ans"));
      if (g === "plus15") ob.push(li("gaz", "installation de plus de 15 ans")); else if (g === "nsp") av.push(li("gaz", "obligatoire si l'installation a plus de 15 ans"));
    } else if (p === "travaux"){
      if (ancien) ob.push(li("amiante", "repérage amiante avant travaux, obligatoire avant d'intervenir sur le bâti"));
      if (tresAncien) av.push(li("plomb", "repérage plomb avant travaux, recommandé pour protéger les intervenants"));
      av.push(li("audit", "utile pour choisir les travaux de rénovation énergétique"));
      if (!ancien) av.push(li("dpe", "pour mesurer le gain après travaux"));
    } else {
      ob.push(li("pppt", "copropriété de plus de 15 ans")); ob.push(li("dpecol", "bâtiment d'habitation collective dont le permis est antérieur à 2013"));
      if (ancien) ob.push(li("amiante", "dossier technique amiante des parties communes"));
      av.push(li("dtg", "obligatoire lors d'une mise en copropriété d'un immeuble de plus de 10 ans, utile avant un programme de travaux"));
    }
    var h = '<div class="qd-out"><h3>Diagnostics à faire réaliser</h3>' + (ob.length ? '<ul>' + ob.join("") + '</ul>' : '<p>Aucun diagnostic obligatoire d\'après vos réponses.</p>');
    if (av.length) h += '<h3>À vérifier ou conseillés</h3><ul>' + av.join("") + '</ul>';
    h += '<p class="note">Liste indicative établie d\'après vos réponses. Nous la confirmons gratuitement avec vous.</p>' +
      '<p><a class="btn" href="tel:+33298463901">📞 Appelez-nous au 02 98 46 39 01</a> <a class="btn clair" href="/devis/">Demander un devis</a></p></div>';
    out.innerHTML = h;
  }
  f.addEventListener("submit", function(e){ e.preventDefault(); calc(); out.scrollIntoView({behavior: "smooth", block: "nearest"}); });
})();
