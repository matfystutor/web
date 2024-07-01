$(document).keypress(function(ev) {
	if (/^[1-9]$/.exec(ev.key)) {
		var optionIndex = parseInt(ev.key);
		var radios = $('#tkgal-container > *:not(.hidden) input[type=radio]');
		var target = radios.eq(optionIndex - 1).val();
		radios.val([target]);
	}
});

function any_visibility_changed() {
	var radios = $('#tkgal-container input[type=radio]').toArray();
	for (var i = 0; i < radios.length; ++i)
		if (radios[i].checked !== radios[i].defaultChecked)
			return true;
	return false;
}

$(window).on('beforeunload', function () {
	if (any_visibility_changed())
		return 'Du mangler at gemme dine ændringer til billedernes synlighed';
});
