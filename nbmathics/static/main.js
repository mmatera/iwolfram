
define(
    function() {
	function _load_ipython_extension(){
	    console.info("init nbmathics");
	    
	    var handlerCtrlEsc = function(){
		var cm = IPython.notebook.get_selected_cell().code_mirror;
		var start = cm.getCursor("start"), end = cm.getCursor("end");
		if (start.line == end.line && start.ch == end.ch){
		    if (handlerCtrlEsc.status != false){
			alert("Closing the selection from " + String(handlerCtrlEsc.status.line) + ":" + String(handlerCtrlEsc.status.ch) +
			      " in " + String(end.line) + ":" + String(end.ch));
			handlerCtrlEsc.status = false;
		    }else{
			var cm = IPython.notebook.get_selected_cell().code_mirror;
			var start = cm.getCursor("start"), to = cm.getCursor("end");
			handlerCtrlEsc.status = start
			alert("Open the selection at " + String(start.line) + ":" + String(start.ch));
		    }
		}else{
		    handlerCtrlEsc.status = false
		    alert("the selection now is from " + String(start.line) + ":" + String(start.ch) +
			      " to " + String(end.line) + ":" + String(end.ch));
		    
		} 
		
		return false;
	    };
	    handlerCtrlEsc.status = false;
	    
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
