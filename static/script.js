function find_portraits() {
	var imgs = document.getElementsByClassName('tutorpicture');
	for (var i = 0, l = imgs.length; i < l; ++i) {
		var img = imgs[i];
		if (img.naturalWidth >= img.naturalHeight) {
			img.style.marginLeft = (img.naturalHeight-img.naturalWidth)/img.naturalHeight * img.clientHeight / 2 + 'px';
		} else {
			img.style.top = (img.naturalWidth-img.naturalHeight)/img.naturalWidth * img.clientHeight / 2 + 'px';
			img.className += ' portrait';
		}
	}
}
window.addEventListener('load', find_portraits, false);
