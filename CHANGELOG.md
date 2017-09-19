# DEV
# 0.0.6
- Add `FRONTEND_URL` default of `DJCORE.SITE_URL`
- Make celery import optional
- Add pre-import to stop alpine segfaults
- Fix DJDT enabling setting use in urls
- Fix nested env var retrieval
- Flatten settings evaluation
- Move module to top-level package
# 0.0.5
- Add psycopg2 as default db backend
- Update anymail backend
- Add second requirements file for defaults
- Update relationship between config and settings
# 0.0.4
- Update celery config defaults with prefix
- Add default SSL forwarding header for SSL behind proxy detection
# 0.0.3
- Improves python2 support
- Adds pyup for requirements management
- Improve app imports
# 0.0.2
- Initial upload
