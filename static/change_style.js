var root = location.protocol + '//' + location.host;

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

function changeStyle() {
    var style = document.getElementById('style');
    if (getCookie('preferredStyle') === 'dark') {
        style.href = root + "/static/light.css";
        setCookie('preferredStyle', 'light', 30); // Store user preference in cookies
    } else {
        style.href = root + "/static/dark.css";
        setCookie('preferredStyle', 'dark', 30); // Store user preference in cookies
    }
}

// On page load, set the style based on the user's preference stored in cookies
window.onload = function() {
    var style = document.getElementById('style');
    var preferredStyle = getCookie('preferredStyle');
    if (preferredStyle === 'light') {
        style.href = root + "/static/light.css";
    } else {
        style.href = root + "/static/dark.css";
    }
};
