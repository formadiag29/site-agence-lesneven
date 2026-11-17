#!/usr/bin/env python3
"""Génère le site statique de l'agence Arliane Diagnostic Immobilier – Lesneven."""
import json, os, re, shutil, html
from datetime import date

BASE = "https://www.sas-liberge.fr"
OUT = "/home/claude/site-agence"
NOM = "Arliane Diagnostic Immobilier – Lesneven"
TEL = "02 98 46 39 01"
TEL_LINK = "+33298463901"
MAIL = "accueil@sas-liberge.fr"
RUE, CP, VILLE = "15 rue Général de Gaulle", "29260", "Lesneven"
LOGO = "https://diagnostic-immobilier-arliane.fr/wp-content/themes/ARLIANE/images/logo-arliane.png"
DEVIS = "/devis/"
TODAY = date.today().isoformat()
AVIS_URL = "https://share.google/TphOHGbXyvr36DbpX"
FICHE_LAN = "https://share.google/anPsgZyXMJUAxXIOB"
FICHES = f'<p class="fiches">Retrouvez-nous sur Google : <a href="{AVIS_URL}" rel="noopener">fiche de l\'agence de Lesneven</a> · <a href="{FICHE_LAN}" rel="noopener">fiche de Lanarvily</a></p>'
AVIS = f'<p class="avis"><span class="etoiles" aria-hidden="true">★★★★★</span> <strong>4,8 / 5</strong> sur Google, 41 avis pour l\'agence de Lesneven · <strong>4,9 / 5</strong>, 39 avis pour notre adresse de Lanarvily. Lire les avis : <a href="{AVIS_URL}" rel="noopener">Lesneven</a>, <a href="{FICHE_LAN}" rel="noopener">Lanarvily</a> <span class="note">(relevé du 17 novembre 2026)</span></p>'

# ---------------------------------------------------------------- contenus
DIAGS = [
 dict(slug="dpe", nom="DPE", titre="Diagnostic de performance énergétique (DPE)",
  desc="DPE à Lesneven et dans le Nord-Finistère : obligatoire pour vendre ou louer, valable 10 ans. Intervention rapide, rapport clair. Devis gratuit.",
  intro="Le DPE classe votre logement de A à G selon sa consommation d'énergie et ses émissions de gaz à effet de serre. Il est obligatoire pour toute vente et toute mise en location, et son étiquette doit figurer dès l'annonce immobilière.",
  quand=["Vente d'une maison ou d'un appartement", "Mise en location ou renouvellement de bail", "Affichage obligatoire de l'étiquette dans l'annonce"],
  validite="10 ans. Les DPE réalisés avant le 1er juillet 2021 ne sont plus valables.",
  plus=[("Un diagnostic opposable", "Depuis le 1er juillet 2021, le DPE engage la responsabilité du vendeur ou du bailleur. Un DPE réalisé avec soin, sur la base de justificatifs, vous protège."),
        ("Passoires thermiques : le calendrier", "Les logements classés G ne peuvent plus être proposés à la location depuis le 1er janvier 2025. Les logements classés F suivront en 2028, puis les E en 2034."),
        ("Ce qui change au 1er janvier 2027", "Le coefficient de conversion de l'électricité passe de 1,9 à 1,7. De nombreux logements chauffés à l'électricité gagnent une classe. <a href=\"/dpe-2027/\">Testez votre DPE avec notre simulateur gratuit</a>.")],
  prepa=["Factures de travaux d'isolation, de chauffage ou de menuiseries", "Notices de la chaudière, de la pompe à chaleur ou du ballon d'eau chaude", "Plans, taxe foncière ou règlement de copropriété si vous les avez"],
  faq=[("Combien de temps dure la visite ?", "Comptez environ une heure pour un appartement et une à deux heures pour une maison, selon la surface et les équipements."),
       ("Mon DPE est mauvais, que puis-je faire ?", "Le rapport contient des recommandations de travaux chiffrées. Pour un projet de rénovation complet, l'audit énergétique va plus loin et propose des scénarios de travaux.")]),
 dict(slug="amiante", nom="Amiante", titre="Diagnostic amiante",
  desc="Diagnostic amiante avant vente, location ou travaux à Lesneven, Brest et dans le Nord-Finistère. Opérateurs certifiés, devis gratuit.",
  intro="L'amiante a été utilisé massivement dans la construction jusqu'à son interdiction en 1997. Le diagnostic repère les matériaux qui en contiennent et évalue leur état de conservation.",
  quand=["Vente d'un bien dont le permis de construire a été délivré avant le 1er juillet 1997", "Location d'un logement en immeuble collectif (dossier amiante des parties privatives)", "Avant des travaux ou une démolition : repérage spécifique obligatoire"],
  validite="Illimitée pour la vente si aucun matériau amianté n'est repéré et si le diagnostic a été réalisé après le 1er avril 2013. Sinon, il doit être refait.",
  plus=[("Avant travaux ou démolition", "Le repérage avant travaux est une mission distincte du diagnostic de vente : il comporte des sondages destructifs sur les zones concernées par le chantier et protège les entreprises qui interviennent."),
        ("Et si de l'amiante est repéré ?", "Le rapport précise l'état des matériaux et les mesures à prendre : simple surveillance, analyse de l'air ou travaux de retrait par une entreprise certifiée.")],
  prepa=["Date du permis de construire", "Anciens diagnostics amiante", "Accès à toutes les pièces, combles, cave et dépendances"],
  faq=[("Le diagnostiqueur fait-il des prélèvements ?", "Oui, en cas de doute sur un matériau, un échantillon est prélevé et analysé par un laboratoire accrédité."),
       ("Ma maison date de 1998, suis-je concerné ?", "Non pour la vente si le permis de construire est postérieur au 1er juillet 1997.")]),
 dict(slug="plomb", nom="Plomb", titre="Diagnostic plomb (CREP)",
  desc="Constat de risque d'exposition au plomb (CREP) pour les logements d'avant 1949 à Lesneven et dans le Nord-Finistère. Devis gratuit.",
  intro="Le constat de risque d'exposition au plomb (CREP) recherche la présence de plomb dans les peintures et revêtements anciens, dangereux en particulier pour les jeunes enfants et les femmes enceintes.",
  quand=["Vente d'un logement construit avant le 1er janvier 1949", "Mise en location d'un logement construit avant le 1er janvier 1949", "Parties communes des immeubles collectifs d'avant 1949"],
  validite="Vente : 1 an si du plomb est détecté au-dessus du seuil réglementaire, illimitée sinon. Location : 6 ans si du plomb est détecté, illimitée sinon.",
  plus=[("Une mesure sans dégradation", "Les mesures sont réalisées avec un appareil à fluorescence X, sans abîmer les peintures ni les boiseries."),
        ("En cas de présence de plomb", "Le rapport classe chaque élément selon son état. Des revêtements dégradés imposent des travaux au propriétaire.")],
  prepa=["Année de construction du logement", "Accès à l'ensemble des pièces, y compris cave et grenier"],
  faq=[("Tous les logements anciens contiennent-ils du plomb ?", "Non, mais c'est fréquent dans les peintures d'avant 1949. Seule la mesure permet de le savoir."),]),
 dict(slug="electricite", nom="Électricité", titre="Diagnostic électricité",
  desc="Diagnostic de l'installation électrique de plus de 15 ans pour vendre ou louer à Lesneven, Brest et dans le Nord-Finistère. Devis gratuit.",
  intro="Le diagnostic électricité vérifie la sécurité de l'installation intérieure : protection, mise à la terre, matériels vétustes ou inadaptés. Il informe l'acquéreur ou le locataire, sans obligation de travaux pour le vendeur.",
  quand=["Vente d'un logement dont l'installation électrique a plus de 15 ans", "Mise en location d'un logement dont l'installation a plus de 15 ans"],
  validite="3 ans pour une vente, 6 ans pour une location.",
  plus=[("Ce qui est contrôlé", "Le tableau électrique, le dispositif différentiel, la mise à la terre, les salles d'eau, les conducteurs et les matériels présentant des risques de contact direct."),
        ("Des anomalies sont relevées ?", "Elles sont listées et expliquées dans le rapport. Pour une location, le logement doit rester décent et sûr : certaines anomalies doivent être corrigées.")],
  prepa=["Accès au tableau électrique et au compteur", "Courant en service le jour de la visite"],
  faq=[("Le diagnostic vaut-il attestation de conformité ?", "Non. Il s'agit d'un état de l'installation à un instant donné, et non d'un certificat de conformité type Consuel."),]),
 dict(slug="gaz", nom="Gaz", titre="Diagnostic gaz",
  desc="Diagnostic de l'installation de gaz de plus de 15 ans pour vendre ou louer à Lesneven et dans le Nord-Finistère. Devis gratuit.",
  intro="Le diagnostic gaz contrôle l'installation intérieure : tuyauteries, raccordements, ventilation des locaux et combustion des appareils. Il vise à prévenir les fuites et les intoxications au monoxyde de carbone.",
  quand=["Vente d'un logement dont l'installation de gaz a plus de 15 ans", "Mise en location d'un logement dont l'installation a plus de 15 ans", "Y compris les installations alimentées par bouteilles ou citerne"],
  validite="3 ans pour une vente, 6 ans pour une location.",
  plus=[("En cas de danger grave", "Si un danger grave et immédiat est constaté, l'alimentation de l'appareil ou de l'installation concernée est coupée et le distributeur est informé."),],
  prepa=["Gaz en service le jour de la visite", "Dernière attestation d'entretien de la chaudière"],
  faq=[("Je n'ai qu'une plaque de cuisson au gaz en bouteille, suis-je concerné ?", "Une installation alimentée par une bouteille raccordée par un simple flexible n'entre pas dans le champ du diagnostic. En cas de doute, appelez-nous."),]),
 dict(slug="etat-parasitaire", nom="État parasitaire", titre="État parasitaire (mérule et insectes du bois)",
  desc="État parasitaire à Lesneven et dans le Nord-Finistère : recherche de mérule, de champignons lignivores et d'insectes xylophages. Réalisé sur tous nos dossiers de vente.",
  intro="L'état parasitaire recherche les agents de dégradation du bois dans le bâtiment : champignons lignivores comme la mérule, insectes à larves xylophages comme le capricorne ou la vrillette. Dans le Nord-Finistère, où le climat humide favorise ces pathologies, nous le réalisons sur tous les biens que nous diagnostiquons.",
  quand=["Vente d'une maison ou d'un appartement : nous le réalisons systématiquement, quel que soit l'âge du bien", "À la demande du notaire, de l'acquéreur ou de la banque", "Avant des travaux sur une charpente, un plancher ou des boiseries", "Dans les communes couvertes par un arrêté préfectoral mérule, où le vendeur doit informer l'acquéreur du risque"],
  validite="Aucune durée n'est fixée par la réglementation. L'usage, suivi par les notaires, est de six mois.",
  plus=[("Ce que nous contrôlons", "Charpente, planchers, solives, plinthes, menuiseries, caves et vides sanitaires. L'examen est visuel, complété par le sondage des bois et des mesures d'humidité, à la recherche d'indices d'infestation et de conditions favorables à leur développement."),
        ("La mérule, un risque bien connu en Bretagne", "Ce champignon se développe dans les bâtiments humides et mal ventilés et dégrade les bois de structure, parfois sans signe visible depuis les pièces de vie. Un état parasitaire permet de lever le doute avant une vente."),
        ("Et les termites ?", "Notre secteur d'intervention n'est pas concerné par les termites : aucun état termites n'y est exigé. C'est l'état parasitaire, plus large, qui répond au risque réel du bâti breton."),
        ("Une mission encadrée par une norme", "L'état parasitaire est réalisé selon la norme NF P 03-200, qui définit la méthode d'investigation et le contenu du rapport.")],
  prepa=["Accès aux caves, vides sanitaires, combles et dépendances", "Dégagement des plinthes et des pieds de murs si possible", "Signalement des dégâts des eaux ou traitements du bois déjà réalisés"],
  faq=[("L'état parasitaire est-il obligatoire ?", "Il n'est pas imposé par la loi, mais il est très souvent demandé par les notaires et les acquéreurs en Bretagne. Il protège le vendeur contre un recours ultérieur pour vice caché. C'est pourquoi nous le réalisons sur tous les biens."),
       ("Que se passe-t-il si de la mérule est détectée ?", "Le rapport localise les zones atteintes. La présence de mérule doit être déclarée en mairie, et le traitement est confié à une entreprise spécialisée, après suppression de la cause d'humidité.")]),
 dict(slug="loi-carrez-boutin", nom="Loi Carrez et Boutin", titre="Mesurage loi Carrez et loi Boutin",
  desc="Mesurage loi Carrez pour la vente d'un lot de copropriété et surface habitable loi Boutin pour la location, à Lesneven et dans le Nord-Finistère.",
  intro="La surface indiquée dans un acte de vente ou un bail vous engage. Le mesurage loi Carrez concerne la vente des lots de copropriété, la surface habitable loi Boutin concerne les locations.",
  quand=["Vente d'un lot de copropriété : surface privative loi Carrez", "Mise en location d'un logement vide ou meublé : surface habitable loi Boutin"],
  validite="Illimitée tant qu'aucuns travaux ne modifient la surface.",
  plus=[("Pourquoi faire mesurer par un professionnel ?", "Si la surface réelle est inférieure de plus de 5 % à celle indiquée dans l'acte, l'acquéreur peut demander une diminution du prix. Le mesurage par un professionnel assuré sécurise la vente."),],
  prepa=["Règlement de copropriété et état descriptif de division", "Accès à toutes les pièces du lot"],
  faq=[("Quelle différence entre Carrez et Boutin ?", "Les deux excluent les surfaces sous 1,80 m de hauteur, mais la surface habitable loi Boutin exclut en plus certains locaux comme les vérandas, combles non aménagés ou sous-sols."),]),
 dict(slug="erp", nom="ERP", titre="État des risques (ERP)",
  desc="État des risques (ERP) pour la vente ou la location à Lesneven et dans le Nord-Finistère : risques naturels, radon, sismicité, pollution des sols.",
  intro="L'état des risques informe l'acquéreur ou le locataire des risques auxquels le bien est exposé : risques naturels, miniers et technologiques, sismicité, potentiel radon, pollution des sols, recul du trait de côte.",
  quand=["Toute vente d'un bien bâti ou non bâti", "Toute mise en location", "Dès l'annonce immobilière et la première visite"],
  validite="6 mois.",
  plus=[("Le radon en Bretagne", "Le sous-sol granitique breton favorise la présence de radon, un gaz radioactif naturel. De nombreuses communes du Finistère sont classées en potentiel radon significatif, ce que l'ERP doit mentionner."),],
  prepa=["Adresse précise et références cadastrales du bien"],
  faq=[("L'ERP doit-il être refait pour chaque locataire ?", "Il doit avoir moins de 6 mois à la signature du bail ou de la promesse de vente."),]),
 dict(slug="audit-energetique", nom="Audit énergétique", titre="Audit énergétique réglementaire",
  desc="Audit énergétique obligatoire pour vendre une maison classée E, F ou G à Lesneven, Brest et dans le Nord-Finistère. Scénarios de travaux chiffrés.",
  intro="L'audit énergétique va plus loin que le DPE : il propose des scénarios de travaux chiffrés pour amener le logement vers une meilleure classe énergétique. Il est obligatoire pour vendre les maisons et immeubles en monopropriété les plus énergivores.",
  quand=["Vente d'une maison individuelle ou d'un immeuble en monopropriété classé F ou G (depuis le 1er avril 2023)", "Vente d'un bien classé E (depuis le 1er janvier 2025)", "Vente d'un bien classé D à partir du 1er janvier 2034", "Projet de rénovation globale, pour choisir les bons travaux"],
  validite="5 ans.",
  plus=[("Ce que contient l'audit", "Un état des lieux du bâti et des équipements, puis au moins deux scénarios de travaux : l'un par étapes, l'autre en une seule fois, avec les gains attendus et une estimation des coûts et des aides."),
        ("DPE 2027 : votre bien est-il encore concerné ?", "Avec le nouveau coefficient de l'électricité, certains logements changent de classe et peuvent sortir de l'obligation d'audit. <a href=\"/dpe-2027/\">Vérifiez avec notre simulateur</a>.")],
  prepa=["DPE existant", "Factures de travaux et notices des équipements", "Plans du logement si vous en disposez"],
  faq=[("L'audit oblige-t-il à faire les travaux ?", "Non. Il informe l'acquéreur, qui reste libre de réaliser ou non les travaux proposés."),
       ("Les appartements sont-ils concernés ?", "Non, l'audit réglementaire à la vente ne concerne pas les lots de copropriété.")]),
 dict(slug="pppt", nom="PPPT", titre="Projet de plan pluriannuel de travaux (PPPT)",
  desc="PPPT obligatoire pour les copropriétés de plus de 15 ans : notre agence de Lesneven accompagne syndics et conseils syndicaux du Nord-Finistère. Devis gratuit.",
  intro="Le projet de plan pluriannuel de travaux (PPPT) dresse la liste des travaux nécessaires à la sauvegarde de l'immeuble, à la sécurité des occupants et aux économies d'énergie, avec un échéancier sur dix ans. Il est désormais obligatoire pour toutes les copropriétés de plus de quinze ans.",
  quand=["Copropriétés de plus de 200 lots : depuis le 1er janvier 2023", "Copropriétés de 51 à 200 lots : depuis le 1er janvier 2024", "Copropriétés de 50 lots ou moins : depuis le 1er janvier 2025", "Immeubles à destination totale ou partielle d'habitation, dont la réception des travaux date de plus de 15 ans"],
  validite="Le PPPT couvre dix ans et doit être actualisé tous les dix ans.",
  plus=[("Ce que contient le PPPT", "La liste des travaux à prévoir, classés par ordre de priorité, une estimation de leur coût, un niveau de performance énergétique visé et une proposition d'échéancier sur dix ans. Il s'appuie sur une analyse du bâti, des équipements et du DPE collectif."),
        ("Du projet au plan voté", "Le projet est présenté en assemblée générale. Si des travaux sont nécessaires, les copropriétaires votent l'adoption de tout ou partie du plan, qui alimente alors le fonds de travaux."),
        ("Notre accompagnement", "Visite complète de l'immeuble, analyse des documents de la copropriété, hiérarchisation et chiffrage des travaux, puis présentation au conseil syndical et en assemblée générale. Nous intervenons en partenariat avec un bureau d'études structure et thermique."),
        ("Petites copropriétés du Nord-Finistère", "De nombreux immeubles de centre-bourg et petites copropriétés sans syndic professionnel sont concernés sans le savoir. Nous vous aidons à faire le point sur vos obligations.")],
  prepa=["Règlement de copropriété, carnet d'entretien, plans", "Derniers procès-verbaux d'assemblée générale et contrats d'entretien", "Diagnostics existants : DPE collectif, amiante des parties communes, DTG éventuel"],
  faq=[("Un DTG dispense-t-il du PPPT ?", "Oui : si le diagnostic technique global ne fait apparaître aucun besoin de travaux dans les dix ans, la copropriété est dispensée d'élaborer un PPPT pendant la durée de validité de ce diagnostic."),
       ("Qui peut réaliser un PPPT ?", "Un professionnel justifiant de compétences et de garanties définies par décret : compétences sur le bâti, les équipements, la thermique, et une assurance adaptée."),
       ("Le PPPT est-il demandé lors d'une vente ?", "Oui, le plan pluriannuel de travaux adopté, ou à défaut le projet de plan, fait partie des documents remis à l'acquéreur d'un lot.")]),
 dict(slug="dtg", nom="DTG", titre="Diagnostic technique global (DTG)",
  desc="Diagnostic technique global (DTG) de copropriété dans le Nord-Finistère : état de l'immeuble, performance énergétique, travaux sur dix ans. Devis gratuit.",
  intro="Le diagnostic technique global (DTG) donne aux copropriétaires une vision complète de leur immeuble : état des parties communes et des équipements, situation au regard des obligations légales, performance énergétique et travaux à prévoir sur dix ans.",
  quand=["Mise en copropriété d'un immeuble de plus de 10 ans : obligatoire", "Immeuble faisant l'objet d'une procédure pour insalubrité, à la demande de l'administration", "Sur décision de l'assemblée générale, pour préparer un programme de travaux"],
  validite="Dix ans pour la dispense de PPPT lorsque le DTG ne révèle aucun besoin de travaux.",
  plus=[("Ce que contient le DTG", "Une analyse de l'état apparent des parties communes et des équipements communs, un état de la situation du syndicat au regard de ses obligations, une analyse des améliorations possibles de la gestion technique, un DPE collectif ou audit énergétique, et une évaluation sommaire du coût des travaux sur dix ans."),
        ("DTG ou PPPT ?", "Le DTG est plus complet que le PPPT. S'il conclut à l'absence de besoin de travaux dans les dix ans, il dispense la copropriété de PPPT. Sinon, il en constitue la base. <a href=\"/diagnostics/pppt/\">En savoir plus sur le PPPT</a>."),
        ("Une équipe pluridisciplinaire", "Nous réalisons le DTG avec un bureau d'études structure et thermique partenaire, pour couvrir le bâti, les équipements et l'énergie.")],
  prepa=["Règlement de copropriété, plans, carnet d'entretien", "Contrats de maintenance et factures de travaux récents", "Diagnostics des parties communes"],
  faq=[("Le DTG est-il obligatoire pour toutes les copropriétés ?", "Non. Il n'est imposé que lors d'une mise en copropriété d'un immeuble de plus de dix ans ou à la demande de l'administration. Les autres copropriétés peuvent le décider en assemblée générale."),]),
 dict(slug="dpe-collectif", nom="DPE collectif", titre="DPE collectif d'immeuble",
  desc="DPE collectif obligatoire pour les immeubles et copropriétés : réalisation dans le Nord-Finistère par notre agence de Lesneven. Devis gratuit.",
  intro="Le DPE collectif évalue la performance énergétique de l'immeuble dans son ensemble : enveloppe, chauffage, eau chaude, ventilation. Il sert de base au plan pluriannuel de travaux et peut permettre d'établir les DPE individuels des lots.",
  quand=["Immeubles en monopropriété et copropriétés de plus de 200 lots : depuis le 1er janvier 2024", "Copropriétés de 50 à 200 lots : depuis le 1er janvier 2025", "Copropriétés de 50 lots ou moins : depuis le 1er janvier 2026", "Bâtiments d'habitation collective dont le permis de construire a été déposé avant le 1er janvier 2013"],
  validite="10 ans, sauf si un DPE réalisé après le 1er juillet 2021 classe l'immeuble en A, B ou C.",
  plus=[("À quoi sert-il ?", "Il identifie les postes de déperdition et les travaux les plus efficaces. C'est la première étape d'un <a href=\"/diagnostics/pppt/\">projet de plan pluriannuel de travaux</a>."),
        ("DPE collectif et DPE des appartements", "Les DPE individuels des lots peuvent être générés à partir des données du DPE collectif, ce qui simplifie les ventes et les mises en location dans l'immeuble.")],
  prepa=["Plans de l'immeuble et descriptif des lots", "Caractéristiques de la chaufferie et contrats d'entretien", "Factures de travaux d'isolation ou de menuiseries"],
  faq=[("Notre immeuble a un chauffage individuel, sommes-nous concernés ?", "Oui. Depuis la réforme, l'obligation de DPE collectif vise tous les bâtiments d'habitation collective, quel que soit le mode de chauffage."),]),
]

VILLES = [
 dict(slug="lesneven", nom="Lesneven", accroche="Notre agence est installée au cœur de Lesneven, 15 rue Général de Gaulle. Vous pouvez nous y rencontrer, déposer vos documents ou régler votre diagnostic sur place.",
      bati="Le centre de Lesneven compte de nombreuses maisons de ville et immeubles anciens, souvent antérieurs à 1949 : le diagnostic plomb et l'amiante y sont fréquemment requis, et l'état parasitaire y est une précaution utile. Les quartiers pavillonnaires plus récents sont surtout concernés par le DPE, l'électricité et le gaz.",
      autour="Le Folgoët, Ploudaniel, Kernilis, Saint-Méen, Plouider, Kerlouan, Guissény, Brignogan-Plages"),
 dict(slug="brest", nom="Brest", accroche="Nous intervenons chaque semaine à Brest et dans sa métropole, pour les particuliers comme pour les agences immobilières, notaires et syndics.",
      bati="Le parc brestois est marqué par les immeubles de la reconstruction et les copropriétés des années 1950 à 1980 : amiante avant vente ou avant travaux, mesurage loi Carrez, DPE et diagnostics des parties communes y sont au cœur des dossiers. Les maisons des quartiers périphériques appellent le plus souvent le DPE et, pour les plus énergivores, l'audit énergétique.",
      autour="Guipavas, Le Relecq-Kerhuon, Gouesnou, Bohars, Guilers, Plouzané"),
 dict(slug="landerneau", nom="Landerneau", accroche="Nous réalisons vos diagnostics immobiliers à Landerneau et dans le pays de Landerneau-Daoulas, avec des délais d'intervention courts.",
      bati="Le centre historique de Landerneau rassemble un bâti ancien en pierre où le plomb, l'amiante et l'état parasitaire sont des sujets récurrents. Les lotissements de la périphérie relèvent davantage du DPE et des diagnostics électricité et gaz.",
      autour="Plouédern, La Roche-Maurice, Pencran, Saint-Thonan, Ploudiry, Dirinon"),
 dict(slug="plabennec", nom="Plabennec", accroche="Plabennec est à quelques minutes de notre agence de Lesneven : nous y intervenons très régulièrement, pour les ventes comme pour les locations.",
      bati="Le secteur de Plabennec est majoritairement composé de maisons individuelles, des longères rénovées aux pavillons récents. Les demandes portent surtout sur le DPE, l'électricité, le gaz et, pour les maisons classées E, F ou G, l'audit énergétique obligatoire à la vente.",
      autour="Bourg-Blanc, Le Drennec, Kersaint-Plabennec, Plouvien, Loc-Brévalaire"),
 dict(slug="landivisiau", nom="Landivisiau", accroche="Nous intervenons à Landivisiau et dans le pays de Landivisiau pour tous vos diagnostics avant vente, location ou travaux.",
      bati="Autour de Landivisiau, le bâti mêle maisons de bourg anciennes, corps de ferme et pavillons. Selon l'âge du bien, le dossier comprend le plomb, l'amiante, les installations électriques et de gaz, le DPE et l'état des risques.",
      autour="Lampaul-Guimiliau, Bodilis, Plounéventer, Saint-Servais, Plouvorn, Guiclan"),
 dict(slug="lannilis", nom="Lannilis et la côte des Abers", accroche="De Lannilis à Plouguerneau, nous couvrons toute la côte des Abers pour vos ventes, locations et locations saisonnières.",
      bati="Le littoral compte de nombreuses résidences secondaires et maisons anciennes exposées à l'humidité : le DPE, l'état des risques et l'état parasitaire y prennent une importance particulière. Nous connaissons les contraintes d'accès des biens occupés ponctuellement et adaptons les rendez-vous.",
      autour="Plouguerneau, Landéda, Tréglonou, Plouguin, Saint-Pabu, Lampaul-Ploudalmézeau"),
]

# tableau vente / location : (diagnostic, slug, concerné, validité vente, validité location)
TABLEAU = [
 ("DPE", "dpe", "Tous les logements", "10 ans", "10 ans"),
 ("Amiante", "amiante", "Permis de construire avant le 1er juillet 1997", "Illimitée si absence d'amiante", "Dossier tenu à disposition (immeubles collectifs)"),
 ("Plomb (CREP)", "plomb", "Logements construits avant 1949", "1 an si présence, illimitée sinon", "6 ans si présence, illimitée sinon"),
 ("Électricité", "electricite", "Installation de plus de 15 ans", "3 ans", "6 ans"),
 ("Gaz", "gaz", "Installation de plus de 15 ans", "3 ans", "6 ans"),
 ("État parasitaire", "etat-parasitaire", "Tous les biens : réalisé systématiquement par notre agence", "6 mois (usage)", "Non requis"),
 ("État des risques (ERP)", "erp", "Tous les biens", "6 mois", "6 mois"),
 ("Loi Carrez", "loi-carrez-boutin", "Lots de copropriété", "Illimitée sauf travaux", "Non requis"),
 ("Surface habitable (Boutin)", "loi-carrez-boutin", "Tous les logements loués", "Non requis", "Illimitée sauf travaux"),
 ("Audit énergétique", "audit-energetique", "Maisons et monopropriétés classées E, F ou G", "5 ans", "Non requis"),
]

SEO = {'dpe': 'Diagnostic DPE', 'amiante': 'Diagnostic amiante', 'plomb': 'Diagnostic plomb (CREP)', 'electricite': 'Diagnostic électricité', 'gaz': 'Diagnostic gaz', 'etat-parasitaire': 'État parasitaire et mérule', 'loi-carrez-boutin': 'Mesurage loi Carrez et Boutin', 'erp': 'État des risques (ERP)', 'audit-energetique': 'Audit énergétique', 'pppt': 'PPPT copropriété', 'dtg': 'Diagnostic technique global (DTG)', 'dpe-collectif': 'DPE collectif'}

# ---------------------------------------------------------------- gabarit
NAV = [("/diagnostics/", "Diagnostics"), ("/quels-diagnostics/", "Quels diagnostics ?"), ("/secteurs/", "Secteurs"),
       ("/professionnels/", "Professionnels"), ("/dpe-2027/", "DPE 2027"), ("/observatoire-dpe-nord-finistere/", "Observatoire DPE"),
       ("/actualites/", "Actualités"), ("/devis/", "Devis"), ("/contact/", "Contact")]
ZONES_PIED = []  # rempli par build_v2
e = html.escape
pages = []  # (chemin, titre) pour sitemap et contrôles

def business_ld():
    return {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": BASE + "/#agence", "name": NOM,
            "url": BASE + "/", "telephone": "+33 2 98 46 39 01", "email": MAIL, "image": [BASE + "/assets/photos/agence-arliane-lesneven.jpg", LOGO], "hasMap": AVIS_URL,
            "address": {"@type": "PostalAddress", "streetAddress": RUE, "postalCode": CP, "addressLocality": VILLE, "addressRegion": "Bretagne", "addressCountry": "FR"},
            "areaServed": ["Lesneven", "Brest", "Landerneau", "Landivisiau", "Plabennec", "Lannilis", "Saint-Pol-de-Léon", "Saint-Renan", "Morlaix", "Nord-Finistère"],
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": o, "closes": c} for o, c in (("09:00", "12:00"), ("14:00", "18:00"))]}

def page(path, title, desc, h1, body, crumbs=None, ld=None, extra_head=""):
    """path : '/dpe/' -> écrit dpe/index.html"""
    url = BASE + path
    lds = [business_ld()] + (ld or [])
    if crumbs:
        items = [("Accueil", "/")] + crumbs
        lds.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]})
        fil = '<nav class="fil" aria-label="Fil d\'Ariane">' + " › ".join(
            (f'<a href="{u}">{e(n)}</a>' if i < len(items) - 1 else f'<span>{e(n)}</span>') for i, (n, u) in enumerate(items)) + "</nav>"
    else:
        fil = ""
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{u}"{cur if path.startswith(u) else ""}>{e(n)}</a>' for u, n in NAV)
    ldhtml = "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>\n" for x in lds)
    doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{e(NOM)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/photos/agence-arliane-lesneven.jpg">
<meta property="og:image:width" content="614">
<meta property="og:image:height" content="490">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#5f8f24">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/style.css">
{ldhtml}{extra_head}</head>
<body>
<a class="saut" href="#contenu">Aller au contenu</a>
<header class="haut">
<div class="large barre">
<a class="logo" href="/" aria-label="{e(NOM)} – accueil"><img src="{LOGO}" alt="Arliane Diagnostic Immobilier" width="186" height="48" onerror="this.outerHTML='<strong>Arliane Diagnostic Immobilier</strong>'"><span>Agence de Lesneven</span></a>
<a class="btn tel" href="tel:{TEL_LINK}">📞 {TEL}</a>
</div>
<nav class="menu" aria-label="Menu principal"><div class="large">{nav}</div></nav>
</header>
<main id="contenu">
<div class="large">{fil}
<h1>{h1}</h1>
{body}
</div>
</main>
<section class="appel">
<div class="large">
<h2>Un diagnostic à faire réaliser ?</h2>
<p>Réponse rapide, devis gratuit et rendez-vous sous quelques jours dans tout le Nord-Finistère.</p>
{AVIS}
<p><a class="btn" href="tel:{TEL_LINK}">📞 Appelez-nous au {TEL}</a> <a class="btn clair" href="{DEVIS}">Demander un devis</a></p>
<p class="note"><a href="/">Retour à l'accueil</a> · <a href="/quels-diagnostics/">Quels diagnostics pour mon bien ?</a></p>
</div>
</section>
<footer class="bas">
<div class="large colonnes">
<div><strong>{e(NOM)}</strong><br>{RUE}<br>{CP} {VILLE}<br><a href="tel:{TEL_LINK}">{TEL}</a><br><a href="mailto:{MAIL}">{MAIL}</a><br>Du lundi au vendredi, 9h-12h et 14h-18h<br><a href="{AVIS_URL}" rel="noopener">Notre fiche Google</a></div>
<div><strong>Diagnostics</strong><br>{"<br>".join(f'<a href="/diagnostics/{d["slug"]}/">{e(d["nom"])}</a>' for d in DIAGS)}</div>
<div><strong>Secteurs</strong><br>{"<br>".join(f'<a href="{u}">{e(n)}</a>' for u, n in ZONES_PIED)}</div>
<div><strong>En pratique</strong><br><a href="/quels-diagnostics/">Quels diagnostics pour mon bien ?</a><br><a href="/vente-location/">Vente ou location</a><br><a href="/projets/">Vos diagnostics par projet</a><br><a href="/professionnels/">Professionnels</a><br><a href="/dpe-2027/">Simulateur DPE 2027</a><br><a href="/observatoire-dpe-nord-finistere/">Observatoire DPE</a><br><a href="/actualites/">Actualités</a><br><a href="/devis/">Devis gratuit</a><br><a href="/agence/">Notre agence</a><br><a href="/contact/">Contact</a><br><a href="/mentions-legales/">Mentions légales</a></div>
</div>
</footer>
</body>
</html>
"""
    dest = os.path.join(OUT, path.strip("/"), "index.html") if path != "/404.html" else os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf8").write(doc)
    if path != "/404.html":
        pages.append((path, title, desc))

def ul(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"
def _svg(inner): return f'<svg class="ico" viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>'
MAISON = '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>'
IMMEUBLE = '<path d="M5 21V4h9v17"/><path d="M14 9h5v12"/><path d="M8 8h3M8 12h3M8 16h3"/><path d="M3 21h18"/>'
ICONS = {
 "dpe": MAISON + '<path d="M13 11l-3 4h4l-3 4"/>',
 "amiante": '<path d="M12 3l9 16H3z"/><path d="M12 10v4"/><circle cx="12" cy="16.5" r=".6"/>',
 "plomb": '<path d="M12 3c3 4 5 7 5 10a5 5 0 0 1-10 0c0-3 2-6 5-10z"/><path d="M10 14a2 2 0 0 0 2 2"/>',
 "electricite": '<path d="M13 2L5 13h6l-1 9 8-11h-6z"/>',
 "gaz": '<path d="M12 3c1 3 5 5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3 0-6 1-9z"/>',
 "etat-parasitaire": '<ellipse cx="12" cy="13" rx="4" ry="5.5"/><path d="M12 7.5V5M9 4l3 1 3-1M8 11H4M8 14H4M8.5 17L5 19M16 11h4M16 14h4M15.5 17l3.5 2M12 9v9"/>',
 "loi-carrez-boutin": '<rect x="3" y="8" width="18" height="8" rx="1"/><path d="M7 8v3M11 8v4M15 8v3M19 8v4"/>',
 "erp": '<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
 "audit-energetique": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M9 16v-3M12 16V9M15 16v-5"/>',
 "pppt": IMMEUBLE + '<path d="M16 3v3M19 3v3"/>',
 "dtg": '<path d="M4 20V5h8v15"/><path d="M7 9h2M7 13h2"/><circle cx="16.5" cy="14.5" r="3.5"/><path d="M19 17l2.5 2.5"/><path d="M2 20h10"/>',
 "dpe-collectif": IMMEUBLE + '<path d="M18 2l-2 3h3l-2 3"/>',
}
def _ico(u):
    m = re.match(r"^/diagnostics/([a-z0-9-]+)/", u)
    return _svg(ICONS[m.group(1)]) if m and m.group(1) in ICONS else ""
def cartes(items): return '<div class="cartes">' + "".join(f'<a class="carte" href="{u}">{_ico(u)}<strong>{e(t)}</strong><span>{e(d)}</span></a>' for u, t, d in items) + "</div>"
def faq_html(faq): return '<h2>Questions fréquentes</h2>' + "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in faq)
def faq_ld(faq): return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in faq]}

def build():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT + "/assets")
    shutil.copy("/home/claude/style_site.css", OUT + "/assets/style.css")
    cartes_diag = [(f'/diagnostics/{d["slug"]}/', d["nom"], d["intro"].split(". ")[0].rstrip(".") + ".") for d in DIAGS]
    cartes_villes = [(f'/secteurs/{v["slug"]}/', v["nom"], "Diagnostics immobiliers à " + v["nom"].split(" et ")[0]) for v in VILLES]

    # ---- accueil
    faq = [("Quels diagnostics sont obligatoires pour vendre ?", "Cela dépend de l'âge du bien, de son type et de sa localisation. Le DPE et l'état des risques sont toujours requis ; s'y ajoutent selon les cas l'amiante, le plomb, l'électricité, le gaz, l'état parasitaire, le mesurage loi Carrez et l'audit énergétique. <a href=\"/vente-location/\">Voir le tableau complet</a>."),
           ("Sous quel délai pouvez-vous intervenir ?", "Nous proposons en général un rendez-vous sous quelques jours. Les rapports vous sont transmis par e-mail."),
           ("Intervenez-vous pour les professionnels ?", "Oui : agences immobilières, notaires, syndics de copropriété, bailleurs et entreprises de travaux. <a href=\"/professionnels/\">Voir notre accompagnement des professionnels</a>.")]
    body = f"""<p class="chapo">Vous vendez, vous louez ou vous préparez des travaux ? Notre agence de Lesneven réalise l'ensemble de vos diagnostics immobiliers obligatoires dans tout le Nord-Finistère, avec des diagnostiqueurs certifiés et des rapports clairs.</p>
<p><a class="btn" href="tel:{TEL_LINK}">📞 {TEL}</a> <a class="btn clair" href="{DEVIS}">Demander un devis gratuit</a></p>
<div class="bandeau"><strong>Nouveau : votre DPE change-t-il de lettre au 1er janvier 2027 ?</strong> Saisissez votre numéro ADEME et découvrez votre future étiquette. <a href="/dpe-2027/">Essayer le simulateur gratuit</a></div>
<h2>Tous vos diagnostics, un seul interlocuteur</h2>
{cartes(cartes_diag)}
<h2>Pourquoi nous confier vos diagnostics ?</h2>
<div class="atouts">
<div><strong>Une agence locale</strong><p>Une équipe basée à Lesneven, qui connaît le bâti du Nord-Finistère et se déplace chez vous rapidement.</p></div>
<div><strong>Des diagnostiqueurs certifiés</strong><p>Chaque diagnostic est réalisé par un opérateur certifié et assuré, comme l'exige la réglementation.</p></div>
<div><strong>Des rapports compréhensibles</strong><p>Nous prenons le temps d'expliquer les résultats et ce qu'ils impliquent pour votre vente ou votre location.</p></div>
<div><strong>La force d'un réseau</strong><p>Membre du réseau national Arliane Diagnostic Immobilier, spécialiste du diagnostic depuis 2007.</p></div>
</div>
<h2>Vente ou location : de quels diagnostics avez-vous besoin ?</h2>
<p>Les diagnostics à fournir ne sont pas les mêmes selon que vous vendez ou que vous louez, et selon l'âge de votre bien. Notre <a href="/vente-location/">tableau récapitulatif</a> vous donne la liste et les durées de validité en un coup d'œil.</p>
<h2>Nous intervenons près de chez vous</h2>
{cartes(cartes_villes)}
{faq_html(faq)}"""
    page("/", "Diagnostic immobilier Lesneven, Brest, Nord-Finistère | Arliane", "Diagnostics immobiliers à Lesneven et dans le Nord-Finistère : DPE, amiante, plomb, électricité, gaz, audit énergétique. Devis gratuit, rendez-vous rapide.",
         "Diagnostic immobilier à Lesneven et dans le Nord-Finistère", body, ld=[faq_ld(faq)])

    # ---- diagnostics
    page("/diagnostics/", "Tous nos diagnostics immobiliers | Arliane Lesneven", "Tous les diagnostics immobiliers de notre agence de Lesneven : DPE, amiante, plomb, électricité, gaz, état parasitaire, Carrez, ERP, audit énergétique, DTG.",
         "Nos diagnostics immobiliers", f"<p class=\"chapo\">Du DPE à l'audit énergétique, nous réalisons tous les diagnostics exigés pour une vente, une location, des travaux ou la gestion d'une copropriété.</p>{cartes(cartes_diag)}<p>Vous ne savez pas lesquels vous concernent ? Consultez notre <a href=\"/vente-location/\">tableau vente ou location</a> ou appelez-nous au <a href=\"tel:{TEL_LINK}\">{TEL}</a>.</p>",
         crumbs=[("Diagnostics", "/diagnostics/")])
    for d in DIAGS:
        autres = [x for x in DIAGS if x is not d][:4]
        body = f"""<p class="chapo">{d['intro']}</p>
<div class="fiche"><div><strong>Durée de validité</strong><p>{d['validite']}</p></div><div><strong>Zone d'intervention</strong><p>Lesneven, Brest, Landerneau, Plabennec, Landivisiau et tout le Nord-Finistère.</p></div></div>
<h2>Quand est-il obligatoire ?</h2>{ul(d['quand'])}
{"".join(f"<h2>{e(t)}</h2><p>{c}</p>" for t, c in d['plus'])}
<h2>Comment préparer la visite ?</h2><p>Pour un diagnostic précis, pensez à préparer :</p>{ul(d['prepa'])}
<p><a class="btn" href="{DEVIS}">Demander un devis pour ce diagnostic</a></p>
{faq_html(d['faq'])}
<h2>Autres diagnostics</h2>{cartes([(f'/diagnostics/{x["slug"]}/', x["nom"], x["titre"]) for x in autres])}"""
        page(f"/diagnostics/{d['slug']}/", f"{SEO[d['slug']]} à Lesneven | Arliane", d["desc"], d["titre"] + " à Lesneven et dans le Nord-Finistère", body,
             crumbs=[("Diagnostics", "/diagnostics/"), (d["nom"], f"/diagnostics/{d['slug']}/")],
             ld=[faq_ld(d["faq"]), {"@context": "https://schema.org", "@type": "Service", "name": d["titre"], "serviceType": d["titre"], "provider": {"@id": BASE + "/#agence"}, "areaServed": "Nord-Finistère", "url": BASE + f"/diagnostics/{d['slug']}/"}])

    # ---- secteurs
    page("/secteurs/", "Secteurs d'intervention Nord-Finistère | Arliane Lesneven", "Notre agence de Lesneven réalise vos diagnostics immobiliers à Brest, Landerneau, Plabennec, Landivisiau, Lannilis et dans tout le Nord-Finistère.",
         "Nos secteurs d'intervention", f"<p class=\"chapo\">Basés à Lesneven, nous nous déplaçons dans tout le Nord-Finistère, de la côte des Abers à la métropole brestoise et au pays de Landivisiau.</p>{cartes(cartes_villes)}<p>Votre commune n'apparaît pas ? Appelez-nous au <a href=\"tel:{TEL_LINK}\">{TEL}</a> : nous intervenons très probablement chez vous.</p>",
         crumbs=[("Secteurs", "/secteurs/")])
    for v in VILLES:
        court = v["nom"].split(" et ")[0]
        body = f"""<p class="chapo">{v['accroche']}</p>
<h2>Le bâti du secteur et les diagnostics les plus demandés</h2><p>{v['bati']}</p>
<h2>Nos diagnostics à {e(court)}</h2>{cartes([(f'/diagnostics/{d["slug"]}/', d["nom"], d["titre"]) for d in DIAGS])}
<h2>Communes voisines desservies</h2><p>{v['autour']}.</p>
<h2>Prendre rendez-vous</h2><p>Appelez-nous au <a href="tel:{TEL_LINK}">{TEL}</a> ou <a href="{DEVIS}">demandez votre devis</a> : nous vous indiquons les diagnostics nécessaires pour votre bien et vous proposons un rendez-vous rapidement.</p>"""
        page(f"/secteurs/{v['slug']}/", f"Diagnostic immobilier {court} : DPE, amiante, plomb | Arliane", f"Diagnostics immobiliers à {court} : DPE, amiante, plomb, électricité, gaz, audit énergétique. Agence locale à Lesneven, devis gratuit.",
             f"Diagnostic immobilier à {v['nom']}", body, crumbs=[("Secteurs", "/secteurs/"), (v["nom"], f"/secteurs/{v['slug']}/")])

    # ---- vente / location
    lignes = "".join(f'<tr><th scope="row"><a href="/diagnostics/{s}/">{e(n)}</a></th><td>{e(c)}</td><td>{e(vv)}</td><td>{e(vl)}</td></tr>' for n, s, c, vv, vl in TABLEAU)
    faq = [("À quel moment faut-il faire réaliser les diagnostics ?", "Le plus tôt possible : l'étiquette du DPE doit figurer dans l'annonce, et le dossier complet doit être annexé à la promesse de vente ou au bail."),
           ("Que risque-t-on sans diagnostics ?", "Le vendeur ne peut pas s'exonérer de la garantie des vices cachés correspondants, et l'acquéreur ou le locataire peut demander une diminution du prix, voire l'annulation de la vente ou du bail.")]
    body = f"""<p class="chapo">Les diagnostics à fournir dépendent de votre projet, de l'âge du bien et de ses équipements. Voici l'essentiel pour une vente et pour une location.</p>
<div class="defile"><table><thead><tr><th scope="col">Diagnostic</th><th scope="col">Biens concernés</th><th scope="col">Validité pour une vente</th><th scope="col">Validité pour une location</th></tr></thead><tbody>{lignes}</tbody></table></div>
<p class="note">Tableau indicatif. Les obligations exactes dépendent de votre bien : nous les vérifions avec vous gratuitement, par téléphone.</p>
<h2>Vous vendez</h2><p>Le dossier de diagnostic technique doit être annexé à la promesse de vente. Pour une maison classée E, F ou G, l'<a href="/diagnostics/audit-energetique/">audit énergétique</a> s'ajoute au DPE. En copropriété, le <a href="/diagnostics/loi-carrez-boutin/">mesurage loi Carrez</a> est indispensable.</p>
<h2>Vous louez</h2><p>Le dossier est annexé au bail. Attention au <a href="/diagnostics/dpe/">DPE</a> : les logements classés G ne peuvent plus être mis en location depuis le 1er janvier 2025, et le calendrier se poursuit pour les classes F puis E.</p>
<h2>Vous préparez des travaux</h2><p>Avant d'intervenir sur un bâtiment dont le permis est antérieur au 1er juillet 1997, un <a href="/diagnostics/amiante/">repérage amiante avant travaux</a> est obligatoire.</p>
{faq_html(faq)}"""
    page("/vente-location/", "Diagnostics obligatoires vente et location | Arliane Lesneven", "Quels diagnostics pour vendre ou louer ? Tableau complet des diagnostics immobiliers obligatoires et de leur durée de validité, par notre agence de Lesneven.",
         "Vente ou location : quels diagnostics obligatoires ?", body, crumbs=[("Vente ou location", "/vente-location/")], ld=[faq_ld(faq)])

    # ---- professionnels
    body = f"""<p class="chapo">Agences immobilières, notaires, syndics, bailleurs, entreprises de travaux : nous sommes le partenaire diagnostic des professionnels de l'immobilier du Nord-Finistère.</p>
<div class="atouts">
<div><strong>Agences immobilières</strong><p>Prise de rendez-vous directe avec vos vendeurs et bailleurs, délais courts, rapports transmis au format numérique pour vos mandats et vos annonces.</p></div>
<div><strong>Notaires</strong><p>Dossiers de diagnostic technique complets et à jour pour vos compromis et vos actes, avec un interlocuteur joignable.</p></div>
<div><strong>Syndics et copropriétés</strong><p><a href="/diagnostics/pppt/">PPPT</a>, <a href="/diagnostics/dtg/">DTG</a>, <a href="/diagnostics/dpe-collectif/">DPE collectif</a>, diagnostics des parties communes et repérages amiante avant travaux.</p></div>
<div><strong>Bailleurs et gestionnaires</strong><p>Suivi des échéances de validité de vos diagnostics et mise à jour avant chaque relocation.</p></div>
<div><strong>Entreprises et maîtres d'ouvrage</strong><p>Repérage amiante avant travaux ou démolition, pour sécuriser vos chantiers et vos équipes.</p></div>
<div><strong>Un outil pour vos clients</strong><p>Notre <a href="/dpe-2027/">simulateur DPE 2027</a> est en accès libre : partagez-le à vos collaborateurs et à vos clients.</p></div>
</div>
<h2>Travaillons ensemble</h2><p>Appelez-nous au <a href="tel:{TEL_LINK}">{TEL}</a> ou écrivez-nous à <a href="mailto:{MAIL}">{MAIL}</a> pour mettre en place un fonctionnement adapté à votre activité.</p>"""
    page("/professionnels/", "Diagnostics immobiliers pour professionnels | Arliane Lesneven", "Partenaire diagnostic des agences immobilières, notaires, syndics et bailleurs du Nord-Finistère : délais courts, DTG, PPPT, amiante avant travaux.",
         "Diagnostics immobiliers pour les professionnels", body, crumbs=[("Professionnels", "/professionnels/")])

    # ---- simulateur DPE 2027
    src = open("/home/claude/site/index.html", encoding="utf8").read()
    bloc = src[src.index('<div id="dpe2027">'):src.rindex("</div>") + 6]
    faq = [("D'où viennent les données ?", "Le simulateur interroge la base publique des DPE de l'ADEME à partir du numéro saisi. Aucune donnée n'est enregistrée par notre agence."),
           ("Le résultat est-il officiel ?", "Non, il s'agit d'une estimation. L'attestation officielle de nouvelle étiquette sera téléchargeable gratuitement sur l'Observatoire DPE-Audit de l'ADEME à partir du 1er janvier 2027."),
           ("Mon logement est chauffé au gaz, est-il concerné ?", "Très peu : seule la part d'électricité de la consommation est recalculée. Le changement de classe concerne surtout les logements chauffés à l'électricité.")]
    body = f"""<p class="chapo">Au 1er janvier 2027, le coefficient de conversion de l'électricité utilisé dans le DPE passe de 1,9 à 1,7. De nombreux logements chauffés à l'électricité vont gagner une classe énergétique, sans travaux. Vérifiez gratuitement ce que cela change pour le vôtre.</p>
<style>#dpe2027 .entete,#dpe2027 .pied{{display:none}}#dpe2027{{margin:24px 0;padding:0;max-width:760px}}</style>
{bloc}
<h2>Pourquoi l'étiquette change-t-elle ?</h2><p>Le DPE exprime la consommation en énergie primaire. Pour l'électricité, chaque kilowattheure consommé est multiplié par un coefficient : 2,3 jusqu'en 2025, 1,9 depuis le 1er janvier 2026 et 1,7 à partir du 1er janvier 2027. La consommation affichée baisse donc mécaniquement pour les logements électriques.</p>
<h2>Ce que cela change pour vous</h2>{ul(["Un logement classé G qui passe en F peut de nouveau être proposé à la location.", "Une maison qui sort des classes E, F ou G n'est plus soumise à l'audit énergétique obligatoire à la vente.", "Une meilleure étiquette valorise votre bien dans l'annonce."])}
{faq_html(faq)}"""
    page("/dpe-2027/", "Simulateur DPE 2027 par numéro ADEME | Arliane Lesneven", "Simulateur gratuit : saisissez le numéro ADEME de votre DPE et découvrez votre étiquette énergie au 1er janvier 2027 (coefficient électricité 1,7).",
         "Simulateur DPE 2027 : votre nouvelle étiquette énergie", body, crumbs=[("DPE 2027", "/dpe-2027/")], ld=[faq_ld(faq)])

    # ---- devis
    sujet = "Demande de devis diagnostic immobilier"
    corps = "Bonjour,%0D%0A%0D%0AJe souhaite un devis pour :%0D%0A- Projet (vente / location / travaux / copropriété) :%0D%0A- Type de bien (maison / appartement / immeuble) :%0D%0A- Adresse du bien :%0D%0A- Surface approximative :%0D%0A- Année de construction :%0D%0A- Chauffage (électricité / gaz / autre) :%0D%0A%0D%0AMes coordonnées :%0D%0A- Nom :%0D%0A- Téléphone :%0D%0A"
    body = f"""<p class="chapo">Dites-nous quel est votre projet : nous vous indiquons les diagnostics réellement nécessaires pour votre bien et nous vous adressons un devis gratuit, sans engagement.</p>
<p><a class="btn" href="tel:{TEL_LINK}">📞 Appelez-nous au {TEL}</a> <a class="btn clair" href="mailto:{MAIL}?subject={sujet.replace(' ', '%20')}&body={corps}">Envoyer une demande par e-mail</a></p>
<div class="atouts">
<div><strong>Un conseil avant tout</strong><p>En quelques minutes au téléphone, nous faisons le point sur vos obligations. Vous ne commandez que les diagnostics utiles.</p></div>
<div><strong>Un rendez-vous rapide</strong><p>Nous intervenons sous quelques jours dans tout le Nord-Finistère.</p></div>
<div><strong>Un dossier complet</strong><p>Tous les diagnostics sont réalisés lors d'une même visite et les rapports vous sont envoyés par e-mail.</p></div>
</div>
<h2>Les informations utiles pour votre devis</h2>{ul(["Votre projet : vente, location, travaux ou copropriété", "Le type de bien et sa surface approximative", "L'année de construction", "Le mode de chauffage et l'âge des installations électriques et de gaz", "L'adresse du bien"])}
<p>Vous ne savez pas quels diagnostics vous concernent ? <a href="/quels-diagnostics/">Répondez à quelques questions</a> pour obtenir la liste.</p>
<p class="note">Du lundi au vendredi, de 9h à 12h et de 14h à 18h.</p>"""
    page("/devis/", "Devis gratuit diagnostic immobilier | Arliane Lesneven", "Devis gratuit et sans engagement pour vos diagnostics immobiliers à Lesneven et dans le Nord-Finistère : par téléphone ou par e-mail, réponse rapide.",
         "Devis gratuit pour vos diagnostics", body, crumbs=[("Devis", "/devis/")])

    # ---- contact
    body = f"""<p class="chapo">Notre équipe vous répond du lundi au vendredi, de 9h à 12h et de 14h à 18h.</p>
<div class="fiche">
<div><strong>Par téléphone</strong><p><a class="btn" href="tel:{TEL_LINK}">📞 {TEL}</a></p></div>
<div><strong>Par e-mail</strong><p><a href="mailto:{MAIL}">{MAIL}</a></p></div>
<div><strong>À l'agence</strong><p>{RUE}<br>{CP} {VILLE}</p><p><a href="https://www.google.com/maps/search/?api=1&query={(RUE + ' ' + CP + ' ' + VILLE).replace(' ', '+')}" rel="noopener">Voir l'itinéraire</a></p></div>
</div>
<figure class="photo etroite"><picture><source type="image/webp" srcset="/assets/photos/agence-arliane-lesneven.webp"><img src="/assets/photos/agence-arliane-lesneven.jpg" width="614" height="490" loading="lazy" alt="Façade de l'agence Arliane Diagnostic Immobilier à Lesneven"></picture><figcaption>Notre agence, 15 rue Général de Gaulle à Lesneven</figcaption></figure>
{FICHES}
<h2>Zone d'intervention</h2><p>Lesneven, Brest, Landerneau, Plabennec, Landivisiau, Lannilis et l'ensemble du Nord-Finistère. <a href="/secteurs/">Voir nos secteurs</a>.</p>"""
    page("/contact/", "Contact et horaires | Arliane Diagnostic Immobilier Lesneven", "Contactez notre agence de diagnostic immobilier à Lesneven : 02 98 46 39 01, 15 rue Général de Gaulle. Du lundi au vendredi, 9h-12h et 14h-18h.",
         "Contacter l'agence de Lesneven", body, crumbs=[("Contact", "/contact/")])

    # ---- mentions légales
    body = f"""<h2>Éditeur du site</h2><p>SAS Liberge, exerçant sous l'enseigne Arliane Diagnostic Immobilier<br>Siège social : 36 Penarguear, 29260 Lanarvily<br>Agence : {RUE}, {CP} {VILLE}<br>Téléphone : {TEL} – E-mail : {MAIL}<br>Forme juridique : société par actions simplifiée<br>Capital social : [À COMPLÉTER]<br>SIREN : [À COMPLÉTER] – RCS : [À COMPLÉTER]<br>N° de TVA intracommunautaire : [À COMPLÉTER]<br>Directeur de la publication : Julien Liberge</p>
<h2>Assurance et certifications</h2><p>Assurance responsabilité civile professionnelle : [ASSUREUR ET N° DE POLICE À COMPLÉTER]<br>Les diagnostiqueurs de l'agence sont certifiés par un organisme accrédité : [ORGANISMES ET N° DE CERTIFICATION À COMPLÉTER]</p>
<h2>Hébergement</h2><p>GitHub Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis.</p>
<h2>Données personnelles</h2><p>Ce site n'utilise ni cookie de suivi ni outil de mesure d'audience. Le simulateur DPE 2027 transmet le numéro ADEME saisi à la base publique de l'ADEME ; il n'est pas enregistré par notre agence. Les informations que vous nous communiquez par téléphone ou par e-mail servent uniquement à traiter votre demande. Vous pouvez exercer vos droits d'accès, de rectification et de suppression en écrivant à {MAIL}.</p>
<h2>Propriété intellectuelle</h2><p>Arliane est une marque du réseau Arliane Diagnostic Immobilier. Les contenus de ce site ne peuvent être reproduits sans autorisation.</p>"""
    page("/mentions-legales/", "Mentions légales | Arliane Diagnostic Immobilier Lesneven", "Mentions légales du site de l'agence Arliane Diagnostic Immobilier de Lesneven : éditeur, hébergeur, données personnelles.",
         "Mentions légales", body, crumbs=[("Mentions légales", "/mentions-legales/")])

    return pages

def finalize():
    global pages
    vu = {}
    for p in pages: vu[p[0]] = p
    pages = list(vu.values())
    # ---- 404, sitemap, robots, CNAME
    page("/404.html", "Page introuvable | Arliane Diagnostic Immobilier Lesneven", "Cette page n'existe pas ou a été déplacée.", "Page introuvable",
         f"<p>Cette page n'existe pas ou a été déplacée.</p><p><a class=\"btn\" href=\"/\">Retour à l'accueil</a></p>", extra_head='<meta name="robots" content="noindex">\n')
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{BASE}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p, _, _ in pages) + "</urlset>\n"
    open(OUT + "/sitemap.xml", "w").write(sm)
    open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    open(OUT + "/CNAME", "w").write("www.sas-liberge.fr\n")
    open(OUT + "/.nojekyll", "w").write("")
    for f in ("favicon.ico", "icon-192.png", "apple-touch-icon.png"): shutil.copy("/home/claude/favicons/" + f, OUT + "/" + f)
    open(OUT + "/google095ac99d20450d98.html", "w").write("google-site-verification: google095ac99d20450d98.html")
    k = open("/home/claude/indexnow_key.txt").read().strip(); open(OUT + f"/{k}.txt", "w").write(k)
    return pages

if __name__ == "__main__":
    build(); print(len(finalize()), "pages")
