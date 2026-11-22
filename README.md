# Sources du site www.sas-liberge.fr (Arliane Diagnostic Nord Finistère - SAS LIBERGE)

Cette branche contient les fichiers internes : générateur, données, photos d'origine.
Elle n'est PAS publiée : le site public est la branche `main`, qui ne contient que les pages générées.

## Régénérer le site

    SITE_OUT=/tmp/site python3 build_v2.py     # génère le site dans /tmp/site
    # puis copier le contenu de /tmp/site à la racine de la branche main

- `build_site.py` : identité (nom commercial, raison sociale, mentions légales `LEGAL`), gabarit, pages prestations, robots.txt, sitemap.
- `build_v2.py` : communes, secteurs, pages fortes (`LOCAL`), page pilier, maillage interne, liens de devis, actualités.
- `ademe_communes.txt` : données ADEME par commune (extraction du 17/11/2026).
- `lastmod.json` : date de dernière modification de chaque page (alimente le sitemap).
- `simulateur-dpe-2027.html` : source du simulateur.

Ne jamais copier ces fichiers dans la branche `main`.
