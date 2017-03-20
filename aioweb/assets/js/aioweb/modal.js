class Modal {
    constructor(id) {
        this.node = document.getElementById(id);
        this.node.addEventListener('click', (e)=> {
            if (e.target.matches('.overlay, .close')) {
                this.hide();
            }
        }, false);
    }

    show() {
        document.body.classList.add('no_scroll');
        this.node.removeAttribute('hidden');
    }

    hide() {
        document.body.classList.remove('no_scroll');
        this.node.setAttribute('hidden', 'hidden')
    }
}

class TabbedModal extends Modal {
    constructor(id) {
        super(id);
        this.form = this.node.querySelector('form');
        if (this.form) {
            this.setupForm(this.form);
        }
        this.errorMessage = document.getElementById('failure_reason');
    }

    setupForm(node) {
        node.onsubmit = this.send.bind(this);
    }

    send(e) {
        e.preventDefault();
        this.switchTab('sending');
        Ajax.submitForm(this.form).then(() => {
            this.switchTab('ok');
            setTimeout(() => {
                this.hide();
            }, 5000)
        }).catch((xhr) => {
            if (xhr.status < 500) {
                this.errorMessage.innerHTML = xhr.responseText;
            } else {
                this.errorMessage.innerHTML = 'неизвестная ошибка';
            }
            this.switchTab('fail');
            setTimeout(() => {
                this.switchTab('form');
            }, 5000)
        });
    }

    switchTab(tabName) {
        let visible = this.node.querySelector(`.tab:not([hidden])`);
        if (visible) {
            visible.setAttribute('hidden', 'hidden');
        }
        let tab = this.node.querySelector(`[data-tab="${tabName}"]`);
        if (tab) {
            tab.removeAttribute('hidden');
        }
    }

    show() {
        this.switchTab('form');
        super.show();
    }

    hide() {
        this.switchTab('form');
        super.hide();
    }
}
