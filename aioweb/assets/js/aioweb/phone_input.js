class Mask {
    static get MOBILE_PHONE() {
        return "+7 (9__) ___ __ __";
    }
}

class MaskedInput {
    constructor(element, mask) {
        this.element = element;
        this.mask = mask;
        this.placeholderIndexes = [];
        this.currentIndex = 0;
        this.filledPlacehodlers = '';

        let lastIndex = -1;
        while (true) {
            let idx = mask.indexOf('_', lastIndex);
            if (idx >= -1) {
                this.placeholderIndexes.push(idx);
                this.placeholderIndexes += '_';
                lastIndex = idx;
            } else {
                break;
            }
        }

        let _this = this;
        element.addEventListener('focus', function () {
            if (!this.value) {
                this.value = _this.mask;
            }
            _this.setCursorAtPlaceholder(_this.currentIndex);
        }, false);
        element.addEventListener('blur', function () {
            if (this.value === _this.mask) {
                this.value = '';
            }
        }, false);
        element.addEventListener('input', function (e) {
            if (e.data) {
                // check selection range
                // delete selected placehodlers
                // insert data at next placehodler
            } else {
                // erasing
                switch (e.keyCode) {
                    case 46:    // delete
                        console.log('del');
                        break;
                    case 8:     // backspace
                        console.log('bsp');
                        break;
                    case 37:    // larr
                        console.log('lar');
                        _this.currentIndex = (_this.currentIndex+1) % _this.filledPlaceholders.length;
                        break;
                    case 39:    // rarr
                        console.log('rar');
                        _this.currentIndex = _this.currentIndex?(_this.currentIndex-1):0 ;
                        break;
                    default:
                        ;
                }
            }
        }, false);
    }

    setCursorAtPlaceholder(placeholderIdx) {
        let idx = this.placeholderIndexes;
        if (idx) {
            this.setSelectionRange(idx, idx);
        }
    }

    fillNextPlacelohder(sym) {

    }

    eraseSymbol(pos) {

    }
}
