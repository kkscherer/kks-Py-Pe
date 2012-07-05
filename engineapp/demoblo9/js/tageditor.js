var tagList = [ {% if tags %}'{{ tags|join:"', '" }}'{% endif %} ];

function tag_post(key, tags) {
	tagDialog.setVisible(true);
	var ted = document.getElementById('tagEditor');
	if (ted) {
		ted.value = tags;
		ted.focus();
		var ac = new goog.ui.AutoComplete.Basic(tagList, ted, true);
	}
}

var tagDialog = new goog.ui.Dialog();
tagDialog.setContent('<textarea id="tagEditor" style="width:330px" aria-haspopup="true"></textarea>');
tagDialog.setTitle('Tags wählen');
tagDialog.setButtonSet(goog.ui.Dialog.ButtonSet.OK_CANCEL);
goog.events.listen(tagDialog, goog.ui.Dialog.EventType.SELECT, function(e) {
	var ted = document.getElementById('tagEditor');
	if (e.key == 'ok') {
		// TODO: Tags absenden
		alert('Tags = ' + ted.value);
	}
}); 
goog.events.listen(window, 'unload', function() {
	goog.events.removeAll();
}); 
