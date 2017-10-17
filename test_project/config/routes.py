def setup(router):
    router.backend('backends.web')
    router.backend('backends.ajax')
