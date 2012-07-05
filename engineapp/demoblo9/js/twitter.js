
var loaderIcon = new Image();
loaderIcon.src = '/img/loadericon.gif';
loaderIcon.style['border'] = '0';
loaderIcon.width = '16px';
loaderIcon.height = '11px';

var twitterIcon = new Image();
twitterIcon.src = '/img/twitter-logo-mini.png';
var twitterIcon0 = new Image();
twitterIcon0.src = '/img/twitter-logo-mini-inactive.png';

var myspaceIcon = new Image();
myspaceIcon.src = '/img/myspace-logo-mini.png';
var myspaceIcon0 = new Image();
myspaceIcon0.src = '/img/myspace-logo-mini-inactive.png';

var yahooIcon = new Image();
yahooIcon.src = '/img/yahoo-logo-mini.png';
var yahooIcon0 = new Image();
yahooIcon0.src = '/img/yahoo-logo-mini-inactive.png';


var browser = (function() {
    var b = navigator.userAgent.toLowerCase();
    return {
        safari: /webkit/.test(b),
        opera: /opera/.test(b),
        msie: /msie/.test(b) && !(/opera/).test(b),
        mozilla: /mozilla/.test(b) && !(/(compatible|webkit)/).test(b)
    };
})();

var readyList = [];
var isReady = false;
var postElBackup = {};

function ready(callback) {
    if (!isReady)
        readyList.push(callback);
    else
        callback.call();
}

function fireReady() {
    isReady = true;
    var fn;
    while (fn = readyList.shift())
        fn.call();
}

function prepareOnReady() {
    if (browser.mozilla || browser.opera) {
        document.addEventListener('DOMContentLoaded', fireReady, false);
    }
    else if (browser.msie) {
        document.write("<scr" + "ipt id=__ie_init defer=true src=//:><\/script>");
        var script = document.getElementById('__ie_init');
        if (script) {
            script.onreadystatechange = function() {
                if (this.readyState != 'complete')
                    return;
                this.parentNode.removeChild(this);
                fireReady.call();
            };
        }
        script = null;
    } else if (browser.safari) {
        var safariTimer = setInterval(function() {
            if (document.readyState == 'loaded' || document.readyState == 'complete') {
                clearInterval(safariTimer);
                safariTimer = null;
                fireReady.call();
            }
        }, 10);
    }
}


function onTwitterPostReady(obj) {
    var postEl = document.getElementById('post_twitter_' + obj.key);
    if (!postEl)
        return;
    if (obj.error) {
    	postEl.innerHTML = postElBackup[obj.key];
    	alert("Beim Twittern ist ein Fehler aufgetreten: " + obj.error)
    }
    else {
    	postEl.innerHTML = 'Getwittert';
    }
};


function postToTwitter(key) {
    window['twitterCallback'] = function(obj) { onTwitterPostReady(obj); }
    ready((function() {
        return function () {
            var postEl = document.getElementById('post_twitter_' + key)
            if (!postEl)
                return;
            postElBackup[key] = postEl.innerHTML;
            postEl.innerHTML = '<img src="/img/loadericon.gif" title="Bitte warten ...">';
            var url = '/twitter/post?key=' + key + '&x=' + Math.random();
            var script = document.createElement('script');
            script.setAttribute('src', url);
            document.getElementsByTagName('head')[0].appendChild(script);
        };
    })());
}


function repostToTwitter(key) {
	if (confirm("Der Post wurde bereits getwittert. Jetzt nochmal twittern?"))
		postToTwitter(key)
}


prepareOnReady();
