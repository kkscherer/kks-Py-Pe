// $Id: cms.js bdb7881e36be 2009/12/16 16:17:13 Oliver Lau <oliver@von-und-fuer-lau.de> $
// Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>


postHasChanged = false;


function preview(key) {
	// TODO: Vorschau implementieren
}

function postHasChangedHandler(inst) {
	postHasChanged = true;
}

function confirm_delete_post(key) {
	if (confirm("Diesen Post wirklich löschen?")) {
		window.location="/delete/"+key+"?goto="+escape(window.location.href);
	}
}

function confirm_delete_resource(key) {
	if (confirm("Diese Ressource wirklich löschen?")) {
		window.location="/unload/"+key+"?goto="+escape(window.location.href);
	}
}

function confirm_exit(url) {
	if (postHasChanged) {
		if (!confirm("Dieser Post wurde geändert. Beim Verlassen des Editors werden die Änderungen nicht gespeichert. Trotzdem verlassen?"))
			return;
	}
	window.location = url;
}
