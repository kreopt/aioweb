def setup(router):
    router.root('auth#index')
    router.post('/',   'auth#login', name='do_login')
    router.delete('/', 'auth#logout', name='logout')
