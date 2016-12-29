
define(
    function() {
	function _load_ipython_extension(){
	    console.info("init nbmathics");

	    var escLitToUTFSymbol = {};
	    escLitToUTFSymbol["ii"] = "";
	    escLitToUTFSymbol["jj"] = "";
	    escLitToUTFSymbol["cross"] = "";
	    escLitToUTFSymbol["*"] = "×";
	    escLitToUTFSymbol["c+"] = "⊕";
	    escLitToUTFSymbol["c*"] = "⊗";
	    escLitToUTFSymbol["&&"] = "∧";
	    escLitToUTFSymbol["||"] = "∨";
	    escLitToUTFSymbol["!"]  = "¬";	    
	    escLitToUTFSymbol["pd"] = "∂";
	    escLitToUTFSymbol["del"] = "∇";
	    escLitToUTFSymbol["sum"] = "∑";
	    escLitToUTFSymbol["prod"] = "∏";
	    escLitToUTFSymbol["int"] = "∫";
	    escLitToUTFSymbol["dd"] = "";
	    escLitToUTFSymbol["DD"] = "";
	    escLitToUTFSymbol["prop"] = "∝";
	    escLitToUTFSymbol["inf"] = "∞";
	    escLitToUTFSymbol["elem"] = "∈";
	    escLitToUTFSymbol["sub"] = "⊂";
	    escLitToUTFSymbol["sup"] = "⊃";
	    escLitToUTFSymbol["un"] = "⋃";
	    escLitToUTFSymbol["inter"] = "⋂";
	    escLitToUTFSymbol["."]  = "·";
	    escLitToUTFSymbol["->"] = "→";
	    escLitToUTFSymbol[":>"] = "";
	    escLitToUTFSymbol["=>"] = "";
	    escLitToUTFSymbol["[["] = "〚";
	    escLitToUTFSymbol["]]"]  = "〛";
	    escLitToUTFSymbol["<"] = "〈";
	    escLitToUTFSymbol[">"]  = "〉";
	    escLitToUTFSymbol["<="] = "≤";
	    escLitToUTFSymbol[">="]  = "≥";
	    escLitToUTFSymbol["dg"]  = "†";
	    escLitToUTFSymbol["ct"]  = "";

	    
	    var handlerCtrlEsc = function(){
		var cm = IPython.notebook.get_selected_cell().code_mirror;
		var start = cm.getCursor("start"), end = cm.getCursor("end");
		if (start.line == end.line && start.ch == end.ch){
		    if (handlerCtrlEsc.status != false){
			newchar = escLitToUTFSymbol[cm.doc.getRange(handlerCtrlEsc.status, end)];
			if (newchar != undefined){
			    cm.doc.replaceRange(newchar, handlerCtrlEsc.status, end);
			}
                        handlerCtrlEsc.status = false;
		    }else{
			var cm = IPython.notebook.get_selected_cell().code_mirror;
			var start = cm.getCursor("start"), to = cm.getCursor("end");
			handlerCtrlEsc.status = start;
		    }
		}else{
		    handlerCtrlEsc.status = false
		    newchar = escLitToUTFSymbol[cm.doc.getRange(start, end)];
		    if (newchar != undefined){
			cm.doc.replaceRange(newchar, start, end);
		    }
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
