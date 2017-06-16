export function asElement(element) {
    if (element instanceof HTMLElement) {
        return element;
    } else if (typeof element === typeof '') {
        return document.getElementById(element);
    }
    throw new TypeError("Element should be instance of HTMLElement or string");
}
export function asElements(element, parent=document) {
    if (typeof element === typeof '') {
        return parent.querySelectorAll(element);
    } else {
        return [element];
    }
}

export function inViewport(el) {

    let r, html;
    if (!el || 1 !== el.nodeType) {
        return false;
    }
    html = document.documentElement;
    r = el.getBoundingClientRect();

    return ( !!r
        && r.bottom >= 0
        && r.right >= 0
        && r.top <= html.clientHeight
        && r.left <= html.clientWidth
    );
}
