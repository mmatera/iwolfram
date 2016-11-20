
define(
    function() {
	function _load_ipython_extension(){
	    console.info('this is my nbextension');
	};
	return {load_ipython_extension: _load_ipython_extension};
    }
)
