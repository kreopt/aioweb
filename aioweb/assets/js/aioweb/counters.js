const yaCntMeta = document.querySelector('meta[name="ya_counter"]');
const gaCntMeta = document.querySelector('meta[name="ga_counter"]');
const yaCnt = yaCntMeta ? `yaCounter${yaCntMeta.getAttribute('content')}` : null;
const gaCnt = gaCntMeta ? `gaCounter${gaCntMeta.getAttribute('content')}` : null;

if (yaCnt) {
    window.sendYa = function (target) {
        if (window[yaCnt] && target) {
            window[yaCnt].reachGoal(target);
        }
    };
    document.body.addEventListener('click', function (e) {
        if (e.target.matches('.counter-ya')) {
            sendYa(this.dataset['yaTarget']);
        }
    }, false);
}

if (gaCnt) {
    window.sendGa = function (target) {
        if (ga && target) {
            ga('send', 'event', ...target.split(';'));
        }
    };
    document.body.addEventListener('click', function (e) {
        if (e.target.matches('.counter-ga')) {
            sendGa(this.dataset['gaTarget']);
        }
    }, false);
}
