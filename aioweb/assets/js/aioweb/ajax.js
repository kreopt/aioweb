class Ajax {
    static async submitForm(form, data='', ajax_header = true) {
        if (!data) {
            data = new FormData(form);
        }
        let headers = new Headers();
        if (ajax_header) {
            headers.append('X-Requested-With', 'XMLHttpRequest');
            let csrfCookie = document.cookie.match(/csrftoken=([\w-]+)/);
            if (csrfCookie) {
                headers.append('X-Csrf-Token', csrfCookie[1]);
            }
        }
        let response = await fetch(form.getAttribute('action'), {
            method: 'POST',
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

    static async post(url, data={}, opts={}) {
        if (opts.ajax_header===undefined) {
            opts.ajax_header = true;
        }
        if (opts.content_type===undefined) {
            opts.content_type = 'application/x-www-form-urlencoded';
        }

        switch (opts.content_type) {
            case 'application/x-www-form-urlencoded':
                data = Object.keys(data).map(k => `${encodeURIComponent(k)}=${encodeURIComponent(data[k])}`).join('&')
                break;
            case 'application/json':
                data = JSON.stringify(data);
                break;
        }

        let headers = new Headers();
        if (opts.accept) {
            headers.set('accept', opts.accept);
        }
        if (opts.ajax_header) {
            headers.append('X-Requested-With', 'XMLHttpRequest');
            headers.set('content-type', opts.content_type);
            let csrfCookie = document.cookie.match(/csrftoken=([\w-]+)/);
            if (csrfCookie) {
                headers.append('X-Csrf-Token', csrfCookie[1]);
            }
        }
        // Object.keys(data).map(k => `${encodeURIComponent(k)}=${encodeURIComponent(data[k])}`).join('&')
        let response = await fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            body: data,
            headers: headers
        });
        if (response.status == 200) {
            return response;
        } else {
            throw new Error(response)
        }
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
