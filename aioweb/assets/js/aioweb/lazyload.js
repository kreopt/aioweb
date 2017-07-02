// Ленивая загрузка изображений
// img[data-src], div[data-lazybg]
function hideLazy() {
    let this$1 = this;

    this.classList.remove('lazy-loading');
    this.classList.remove('tagged');

    setTimeout(function (){
        this$1.style.willChange='';
    }, 300);
}

function watchElement(el, watcher) {
    let imgSrc =  el.dataset['src'];
    let img = new Image();
    /* preloading image */
    img.onload = function() {
        if (el.tagName == 'DIV') {
            el.style.backgroundImage = "url('" + imgSrc  + "')"; 
        } else {
            el.src = imgSrc;
        }
        el.style.willChange='opacity';
        // На маленькие изображения, которые грузятся изначально, можно добавить 
        // блюр через класс .blur. После загрузки основной картинки блюр убирается.
        el.classList.remove('blur');
        watcher.destroy();
    };
    img.src = imgSrc;
}

window.initLazy = function(parent) {
    let elements = parent.querySelectorAll('img[data-src], div[data-src]');
    for (let i = 0; i < elements.length; i++){
        let el = elements[i];
        let watcher = scrollMonitor.create(el);
        watcher.enterViewport(watchElement.bind(this, el, watcher));
    }
};

window.lazyLoadAlpha = function(parent) {
    let elements = (parent||document).querySelectorAll('.lazy-loading:not(.tagged)');
    for (let i = 0; i < elements.length; i++){
        let el = elements[i];
        el.classList.add('tagged');
        el.onload = hideLazy;
    }
};
