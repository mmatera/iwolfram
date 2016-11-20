
define(
    function() {
	function _load_ipython_extension(){
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
	    var action_name = 'open-close-symbol';
	    var full_action_nameCtrlEsc = Jupyter.actions.register(actionCtrlEsc, action_nameCtrlEsc, prefix);
	    Jupyter.toolbar.add_buttons_group([full_action_nameCtrlEsc]);
	    Jupyter.keyboard_manager.command_shortcuts.add_shortcut('Ctrl-Esc','nbmathics:open-close-symbol');
	    console.info('this is my nbextension');
	};
	return {load_ipython_extension: _load_ipython_extension};
    }
)
