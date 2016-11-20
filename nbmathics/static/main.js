
define(
    function() {
	function _load_ipython_extension(){
	    alert("init nbmathics");
	    var handlerCtrlEsc = function(){
		alert("You press CtrlEsc");
	    };
	    var actionCtrlEsc = {
		icon: 'fa-comment-o',
		help: 'Show an alert',
		help_index: 'zz',
		handler: handlerCtrlEsc
	    };
	    var prefix = 'nbmathics';
	    var action_nameCtrlEsc = 'open-close-symbol';
	    console.info('nbmathics: Registering action');
	    var full_action_nameCtrlEsc = Jupyter.actions.register(actionCtrlEsc, action_nameCtrlEsc, prefix);
	    console.info('nbmathics: adding button to the toolbar');
	    Jupyter.toolbar.add_buttons_group([full_action_nameCtrlEsc]);
	    console.info('nbmathics: adding keybinding');
	    Jupyter.keyboard_manager.edit_shortcuts.add_shortcut('Ctrl-Esc','nbmathics:open-close-symbol');
	    console.info('this is my nbextension... done');
	};
	return {load_ipython_extension: _load_ipython_extension};
    }
)
