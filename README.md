# Site de l'agence Arliane Diagnostic Nord Finistère (SAS LIBERGE) - Lesneven

Site statique publié sur https://www.sas-liberge.fr (GitHub Pages).

Ne pas modifier les pages à la main : modifier les sources dans `_source/` puis régénérer.

    SITE_OUT=/tmp/site python3 _source/build_v2.py   # génère le site dans /tmp/site
    cp -a /tmp/site/. .                              # puis copier à la racine du dépôt

- `_source/build_site.py` : identité (nom commercial, raison sociale, mentions légales `LEGAL`), gabarit, pages prestations, robots.txt, sitemap.
- `_source/build_v2.py` : communes, secteurs, pages locales (Brest, Plabennec, Lesneven : `LOCAL`), maillage interne, actualités.
- `_source/ademe_communes.txt` : données ADEME par commune.
- `_source/lastmod.json` : date de dernière modification de chaque page (mise à jour automatiquement, alimente le sitemap).

Sauvegarde de l'état avant optimisation SEO du 22/11/2026 : branche `sauvegarde-avant-seo-2026-11-22`.
