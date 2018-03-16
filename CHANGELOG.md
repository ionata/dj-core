# DEV
# 0.1.2
- Add django-storages' AWS_S3_CUSTOM_DOMAIN
- Update dependencies in requirements
# 0.1.1
- Add SERVER_EMAIL to default settings
# 0.1.0
- Update dependencies in requirements-defaults
- Remove Django 2.0 incompatible url config
# 0.0.11
- Add autodiscover for celery tasks
# 0.0.10
- Update to django-anymail~=1.0.0
# 0.0.9
- Fix bug that overrides defaults in get_admin()
# 0.0.8
- Add ability to pass default values to get_admin()
- Make skeleton_data work with custom USERNAME_FIELD
# 0.0.7
- Fail loudly when DefaultProxy.func is None
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
