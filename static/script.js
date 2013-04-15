function find_portraits() {
	var imgs = document.getElementsByClassName('tutorpicture');
	for (var i = 0, l = imgs.length; i < l; ++i) {
		var img = imgs[i];
		if (img.naturalWidth >= img.naturalHeight) continue;
		img.style.top = (img.naturalWidth-img.naturalHeight)/img.naturalWidth * img.clientHeight / 2 + 'px';
		img.className += ' portrait';
	}
}
window.addEventListener('load', find_portraits, false);

function click_to_focus() {
	if (document.body.className.indexOf('tutors') == -1) return;
	var addys = document.getElementsByClassName('tutoraddress');
	var focused = null;
	var focusedClass = '';
	for (var i = 0, l = addys.length; i < l; ++i) {
		addys[i].addEventListener('click', function (event) {
			if (focused != this) {
				if (focused) focused.className = focusedClass;
				focused = this;
				focusedClass = this.className;
				this.className += ' selected';
			}
			event.stopPropagation();
		}, false);
	}
	document.documentElement.addEventListener('click', function (event) {
		if (focused) focused.className = focusedClass;
		focused = null;
	}, false);
}
window.addEventListener('load', click_to_focus, false);
