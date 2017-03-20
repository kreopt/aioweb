class Ajax {
    static async submitForm(form, data='', ajax_header = true) {
        if (!data) {
            data = new FormData(form);
        }
        let headers = new Headers();
        if (ajax_header) {
            headers.append('X-Requested-With', 'XMLHttpRequest');
        }
        let response = await fetch(form.getAttribute('action'), {
            medhod: 'POST',
            credentials: 'same-origin',
            body: data,
            headers: headers
        });
        if (response.status == 200) {
            form.reset();
            return response.text();
        } else {
            throw new Error(response)
        }
    }

    static async loadPage(url, container) {
        let response = await fetch(url, {
            headers: new Headers({'X-Requested-With': 'XMLHttpRequest'}),
            credentials: 'same-origin'
        });
        asElement(container).innerHTML = await response.text();
    }
}

document.body.addEventListener('click', function (e) {
    if (e.target.matches('a[data-ajaxpage-to]')) {
        e.preventDefault();
        let container = document.getElementById(e.target.dataset.ajaxpageTo);
        if (container) {
            let url = e.target.getAttribute('href');
            Ajax.loadPage(url, container).then(()=>{
                // TODO: title
                window.history.pushState('','', url);
            });
        }
    }
});
