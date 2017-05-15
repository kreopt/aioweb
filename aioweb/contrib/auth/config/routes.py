def setup(router):
    router.root('auth#index')
    router.post('/', 'auth#login', name='do_login')
    router.post('/logout', 'auth#logout', name='logout')
