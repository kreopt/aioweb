class OperationButton {
    constructor(selector, parent=document) {
        this.btn = asElements(selector, parent);
    }

    start() {
        if (this.btn && this.btn.length) {
            for (let i = 0; i < this.btn.length; ++i) {
                let btn = this.btn[i];
                btn.setAttribute('disabled', 'disabled');
                btn.classList.add('pending_operation');
            }
        }
    }

    stop() {
        if (this.btn && this.btn.length) {
            for (let i = 0; i < this.btn.length; ++i) {
                let btn = this.btn[i];
                btn.removeAttribute('disabled');
                btn.classList.remove('pending_operation');
            }
        }
    }
}

class FileUploader {
    constructor(cont) {
        this.fileId = 0;
        this.filesCont = cont;
        $(this.filesCont).on('click', '.attachment-delete', function (e) {
            let id = this.parentNode.dataset['id'];
            $(this.parentNode).remove();
        });
    }

    loadend(reader, file) {
        let hdl = ++this.fileId;
        let tpl = Template.render('file_entry_tpl', {
            name: file.name,
            id: hdl
        });
        let entry = document.getElementById('file_entry');
        entry.setAttribute('name', 'files');
        entry.onchange = null;
        let entryParent = entry.parentNode;
        entry.removeAttribute('id');
        tpl.querySelector('.attachment').appendChild(entry);
        let newEntry = document.createElement('input');
        newEntry.setAttribute('id', 'file_entry');
        newEntry.setAttribute('hidden', 'hidden');
        newEntry.setAttribute('type', 'file');
        let uploader = this;
        $(newEntry).on('change', function () {
            uploader.readFiles(this.files);
        });
        entryParent.appendChild(newEntry);
        this.filesCont.appendChild(tpl);
        return hdl;
    }

    removeFile(hdl) {
        this.files.erase(hdl);
    }

    readFiles(files) {
        for (let i = 0; i < files.length; ++i) {
            let file = files[i];
            let reader = new FileReader();
            if (file) {
                reader.onloadend = this.loadend.bind(this, reader, file);
                reader.readAsDataURL(file);
            }
        }
    }
}
