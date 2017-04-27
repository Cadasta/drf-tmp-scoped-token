# DRF Temporary Permissions Token

rest_framework_tmp_perms_token provides a Django REST Framework-compatibale system to generate and validate signed authorisation tokens. Generated tokens contain the ID of a user on whose behalf the token bearer authenticates, a white-list of HTTP verbs and API endpoints that the bearer is permitted to access, an max-lifespan of the token,
and a note about the intended recipient.
