from __future__ import print_function
from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u
from metakernel.process_metakernel import TextOutput
from metakernel.pexpect import EOF, spawnu
# from .pexpect import myspawn

from pexpect.exceptions import TIMEOUT

from IPython.display import Image, SVG
from IPython.display import Latex, HTML, Javascript
from IPython.display import Audio

import subprocess
import os
import sys
import tempfile

import base64

__version__ = '0.0.0'

Widget = None

try:
    from .config import mathexec
except Exception:
    mathexec = "mathics"


if Widget is None:
    try:
        from ipywidgets.widgets.widget import Widget
    except ImportError:
        pass


class MMASyntaxError(BaseException):
    def __init__(self,text, val=0, name="", traceback=None):
        self.val = val
        self.name = name
        self.text = text
        self.traceback = traceback
        self.kernel_type = None


checkjsgraph = """
if (typeof(drawGraphics3D) == "undefined"){
if(document.getElementById("graphics3dScript2") == null){
	       var tagg = document.createElement('script');
               tagg.type = "text/javascript";
               tagg.src = "/nbextensions/nbmathics/static/js/three/Three.js";
               tagg.charset = 'utf-8';
               tagg.id = "graphics3dScript2"
               document.getElementsByTagName("head")[0].appendChild( tagg );
               /*****************************/
	       var tagg = document.createElement('script');
               tagg.type = "text/javascript";
               tagg.src = "/nbextensions/nbmathics/static/js/three/Detector.js";
               tagg.charset = 'utf-8';
               tagg.id = "graphics3dScript2"
               document.getElementsByTagName("head")[0].appendChild( tagg );
               /*****************************/
               var tagg = document.createElement('script');
               tagg.type = "text/javascript";
               tagg.src = "/nbextensions/nbmathics/static/js/graphics3d.js";
               tagg.charset = 'utf-8';
               tagg.id = "graphics3dScript"
               document.getElementsByTagName("head")[0].appendChild( tagg );
   	       console.info('   graphics3dScript loaded.');
            } else{
	       console.info('  graphics3dScript already loaded.');
            }
}
 """


class WolframKernel(ProcessMetaKernel):
    implementation = 'Wolfram Mathematica Kernel'
    implementation_version = __version__,
    language = 'mathematica'
    language_version = '10.0',
    banner = "Wolfram Mathematica Kernel"
    language_info = {
        'exec': mathexec,
        'mimetype': 'text/x-mathics',
        'codemirror_mode': 'mathematica',
        'name': 'Mathematica',
        'file_extension': '.m',
        'help_links': MetaKernel.help_links,
        'version': '0.0.0',
    }

    kernel_json = {
        'argv': [sys.executable, '-m', 'wolfram_kernel',
                 '-f', '{connection_file}'],
        'display_name': 'Wolfram Mathematica',
        'language': 'mathematica',
        'name': 'wolfram_kernel',
    }

    kernel_js ="""
    define(function(){return {onload: function(){
    console.info('wolfram kernel stub loaded');
    if(Jupyter.notebook.kernel.name!="wolfram_kernel"){
        console.info("  Current kernel is not a wolfram_kernel");return;}
    /*Handle Ctrl-Esc symbols */
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
	    escLitToUTFSymbol["<|"] = "";
	    escLitToUTFSymbol["|>"] = "";
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
	console.info('kernel.js wolfram: Registering action');
	var full_action_nameCtrlEsc = Jupyter.actions.register(actionCtrlEsc, action_nameCtrlEsc, prefix);
	console.info('kernel.js: adding button to the toolbar');
	    Jupyter.toolbar.add_buttons_group([full_action_nameCtrlEsc]);
	    console.info('kernel.js: adding keybinding');
	    Jupyter.keyboard_manager.edit_shortcuts.add_shortcut('Ctrl-Esc','nbmathics:open-close-symbol');

	if(document.getElementById("graphics3dScript2") == null){
	       var tagg = document.createElement('script');
               tagg.type = "text/javascript";
               tagg.src = "/nbextensions/nbmathics/static/js/three/Three.js";
               tagg.charset = 'utf-8';
               tagg.id = "graphics3dScript2"
               document.getElementsByTagName("head")[0].appendChild( tagg );
               /*****************************/
	       var tagg = document.createElement('script');
               tagg.type = "text/javascript";
               tagg.src = "/nbextensions/nbmathics/static/js/three/Detector.js";
               tagg.charset = 'utf-8';
               tagg.id = "graphics3dScript2"
               document.getElementsByTagName("head")[0].appendChild( tagg );
               /*****************************/
               var tagg = document.createElement('script');
               tagg.type = "text/javascript";
               tagg.src = "/nbextensions/nbmathics/static/js/graphics3d.js";
               tagg.charset = 'utf-8';
               tagg.id = "graphics3dScript"
               document.getElementsByTagName("head")[0].appendChild( tagg );
   	       console.info('   graphics3dScript loaded.');
            } else{
	       console.info('  graphics3dScript already loaded.');
            }
    }}});
    """

    def get_usage(self):
        return "This is the Wolfram Mathematica kernel."

    def repr(self, data):
        return data

    _session_dir = ""
    _first = True
    initfilename = os.path.dirname(__file__) + "/init.m"
    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            banner = "mathics 0.1"
            self._banner = u(banner)
        return self._banner

    def check_wolfram(self):
        starttext = os.popen("bash -c 'echo |" +
                             self.language_info['exec'] + "'").read()
        if starttext[:11] == "Mathematica":
            self.kernel_type = "wolfram"
        elif starttext[:8] == "\nMathics":
            self.kernel_type = "mathics"
        elif starttext[:21] == "Welcome to Expreduce!":
            self.kernel_type = "expreduce"
        else:
            raise ValueError
        return self.kernel_type

    def __init__(self, *args, **kwargs):
        super(WolframKernel, self).__init__(*args, **kwargs)
        self.bufferout = ""

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        # self.log.warning("help required")
        if none_on_fail:
            return None
        else:
            return "Sorry, no help is available on '%s'." % info['code']

    def show_warning(self, warning):
        self.send_response(self.iopub_socket, 'stream',
                           {'wait': True, 'name': "stderr", 'text': warning})
        return

    def stream_handler(self, strm):
        self.log.warning("stream: {{" + strm + "}}")        
        if len(self.bufferout) == 0:
            if len(strm.strip()) == 0:
                return
            else:
                if strm[0] != 'M' and strm[0] != 'P' and  \
                   not(len(strm) >= 4 and strm.strip()[:4] == "Out["):
                    print(strm)
                    return
        self.bufferout = self.bufferout + strm + "\n"
        offset = 0
        while len(self.bufferout) > offset and self.bufferout[offset] in ("\n", " "):
            offset = offset + 1
            if len(self.bufferout) == offset:
                return
        idx = 2 + offset
        if self.bufferout[offset:idx] == "P:":
            while self.bufferout[idx] != ":":
                idx = idx + 1
            lenmsg = self.bufferout[(offset+2):idx]
            idx = idx + 1
            endpos = idx + int(lenmsg) + 1
            if len(self.bufferout) < endpos:
                return
            else:
               msg = self.bufferout[idx:endpos]
               self.bufferout = self.bufferout[endpos:]
               print(msg)
        elif self.bufferout[offset:idx]=="M:":
            while self.bufferout[idx]!=":":
                idx = idx + 1
            lenmsg = self.bufferout[(offset+2):idx]
            idx = idx + 1
            endpos = idx + int(lenmsg) + 1
            if len(self.bufferout) < endpos:
                return
            else:
               msg = self.bufferout[idx:endpos]
               self.bufferout = self.bufferout[endpos:]
               if msg[:65] == "ToExpression::sntxi: Incomplete expression; more input is needed " or \
                  msg[:48] == "ToExpression::sntx: Invalid syntax in or before ":
                   self.log.warning("incomplete")
                   raise MMASyntaxError("Syntax::sntxi", -1, "sntxi")
               if msg[0:8] == "Syntax::":
                   for p in range(len(msg)):
                       if msg[p] == ":":
                           break
                   raise MMASyntaxError(msg[0:p], -1,
                                                     msg[p+1:])
               elif msg[0:11] == "Power::infy":
                   raise MMASyntaxError(msg[0:11],
                                                     msg[13:])
               elif msg[0:18] == "OpenWrite::noopen":
                   raise MMASyntaxError(msg[0:18],
                                                     msg[20:])
        return

    def print(self, msg):
        self.send_response(self.iopub_socket, 'stream',
                           {'wait': True, 'name': "stdout", 'text': msg})
        return

    def makeWrapper(self):
        """
        Start a math/mathics kernel and return a :class:`REPLWrapper` object.
        """
        self.js_libraries_loaded = False
        orig_prompt = u('In\[.*\]:=')
        prompt_cmd = None
        change_prompt = None
        self.check_wolfram()

        if self.kernel_type in ["wolfram", "expreduce"]:
            self.process_response=self.process_response_wolfram
            self.open_envel = "ToExpression[\"Identity["
            self.close_envel = "]\"]"
            cmdline = self.language_info['exec'] + " -rawterm -initfile '" + self.initfilename + "'"
        elif self.kernel_type in ["mathics"]:
            self.process_response=self.process_response_mathics
            self.open_envel = "$PrePrint[ToExpression[\"Identity["
            self.close_envel = "]\"]]"
            cmdline = self.language_info['exec'] + " --colors NOCOLOR --persist '" + self.initfilename + "'"


        self.myspawner = spawnu(cmdline, errors="ignore", echo=False)
        replwrapper = REPLWrapper(self.myspawner, orig_prompt, change_prompt,
                                  prompt_emit_cmd=None, echo=False)
        return replwrapper

    def do_execute_direct(self, code):
        self.payload = []
        codelines = [codeline.strip() for codeline in code.splitlines()]
        # Remove every empty line at the end of the cell
        while len(codelines)>0  and codelines[-1].strip() == "":
            del codelines[-1]

        lastcommand = ""
        i=0
        lencodelines = len(codelines)
        # Go through each line in the input
        while i < lencodelines:
            self.log.warning("processing line " + str(i) +": <<"+ codelines[i] +">>")
            if codelines[i].strip() == "" and lastcommand == "":
                i += 1
                continue
            lastcommand += codelines[i]
            i = i + 1
            # continue until the end of the current command
            while i <= lencodelines:
                # If the line is empty, check if we have now a complete command
                if i == lencodelines:
                    self.log.warning("   [end of the cell]")
                else:
                    self.log.warning("   processing next line " + str(i) +": <<"+ codelines[i] +">>")
                if i == lencodelines or codelines[i].strip() == "" :
                    try:
                        self.log.warning("trying line...<<"+ lastcommand +">>")
                        resp = self.do_execute_direct_single_command(lastcommand, 
                                              stream_handler=self.stream_handler)
                        self.log.warning("  output:<<"+resp.__str__() +">>")
                        resp = self.postprocess_response(resp.output)
                        self.log.warning("  postprocess output:<<"+resp.__str__()+">>")
                        i = i + 1
                        if i < lencodelines:
                            self.log.warning("OK. Post execution ...")
                            self.post_execute(resp, lastcommand, False)
                        lastcommand = ""
                        break
                    except MMASyntaxError as e:
                        # if the error is due to unbalanced  parentheses or open string ,
                        if e.name == "sntxi":
                            self.wrapper.run_command("$Line=$Line-2;", timeout=None,
                                                 stream_handler=None)
                            if i < lencodelines:
                                lastcommand += "\n" + codelines[i]
                                i += 1
                                continue
                            else:
                                self.kernel_resp = {
                                    'status': 'error',
                                    'execution_count': self.execution_count,
                                    'ename': e.name, 'evalue': e.val,
                                    'traceback': e.traceback,
                                }
                                return TextOutput("null:")
                        else:
                            self.log.warning("Post processing line after exception...")
                            self.post_execute(resp, lastcommand, False)
                            lastcommand = ""
                            i += 1 
                            break
                else:
                    if i < lencodelines:
                        lastcommand += "\n" + codelines[i]
                        i += 1
                        self.log.warning("lastcommand=<<"+lastcommand+">>")
        return resp


    def do_execute_direct_single_command(self, code, stream_handler=None, envelop=True):
        """Execute the code in the subprocess.
        Use the stream_handler to process lines as they are emitted
        by the subprocess.
        """
        self.payload = []
        if not code.strip():
            self.kernel_resp = {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
            return
        interrupted = False
        output = ''
        if envelop:
            code = code.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n","\\n")
            if code.strip()[-1] == ";":
                code = self.open_envel +  code + self.close_envel + ";"
            else:
                code = self.open_envel + code + self.close_envel

        # Ugly, but I didn't find another effective way to clean properly the buffer
        try:
            remaining = ""
            while True:
                remaining += self.myspawner.read_nonblocking(100,.1)
                self.log.warning("      remaining: <<" + remaining +">>")
        except TIMEOUT as e:
            self.log.warning(" empty")
    
        try:
            self.bufferout = ""
            self.log.warning("Sending the comamnd <<" + code +">>")                                        
            output = self.wrapper.run_command(code, timeout=None,
                                              stream_handler=stream_handler)
            self.log.warning("      output single line:<<" + output +">>")
            self.log.warning("      in buffer:<<" + self.bufferout +">>")
            self.log.warning("      myspawn: \n" + self.myspawner.__str__())
            if (stream_handler is not None):
                output = self.bufferout + output
                self.bufferout = ""
            
            output = self.process_response(output)
            self.bufferout = ""

        except MMASyntaxError as e:
            self.log.warning("exception: " + e.__str__())
            if e.name == "sntxi":
                raise e
            else:
                self.kernel_resp = {
                    'status': 'error',
                    'execution_count': self.execution_count,
                    'ename': e.name, 'evalue': e.val,
                    'traceback': e.traceback,
                }
                return TextOutput("null:")
        except KeyboardInterrupt as e:
            interrupted = True
            output = self.wrapper.child.before
            if 'REPL not responding to interrupt' in str(e):
                output += '\n%s' % e
        except EOF:
            output = self.wrapper.child.before + 'Restarting'
            self._start()

        if interrupted:
            self.kernel_resp = {
                'status': 'abort',
                'execution_count': self.execution_count,
            }

        exitcode, trace = self.check_exitcode()
        if exitcode:
            self.kernel_resp = {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': '', 'evalue': str(exitcode),
                'traceback': trace,
            }
        else:
            self.kernel_resp = {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
        return TextOutput(output)

    def process_response_wolfram(self, resp):
        """
        This routine splits the output from messages
        and prints generated before it, and send the corresponding messages.
        It would be better to capture them on the flight, at the very moment
        when the process print them, but it would involve a
        change in the wrapper.
        """
        lineresponse = resp.splitlines()
        outputfound = False
        messagefound = False
        messagetype = None
        messagelength = 0
        lastmessage = ""
        mmaexeccount = -1
        outputtext = "null:"
        sangria = 0
        for linnum, liner in enumerate(lineresponse):
            if outputfound:
                if liner.strip() == "":
                    continue
                if liner.strip()[:4] == "Out[":
                    break
                outputtext = outputtext + liner
            elif messagefound:
                lastmessage = lastmessage + "\n" + liner
                if len(lastmessage) >= messagelength:
                    if messagetype == "M":
                        self.show_warning(lastmessage)
                        if msg[:65] == "ToExpression::sntxi: Incomplete expression; more input is needed " or \
                           msg[:48] == "ToExpression::sntx: Invalid syntax in or before ":
                            raise MMASyntaxError("Syntax::sntxi", -1, "sntxi")
                        if lastmessage[0:8] == "Syntax::":
                            for p in range(len(lastmessage)):
                                if lastmessage[p] == ":":
                                    break
                            raise MMASyntaxError(lastmessage[0:p], -1,
                                                 lastmessage[p+1:])
                        if lastmessage[0:11] == "Power::infy":
                            raise MMASyntaxError(lastmessage[0:11],
                                                 lastmessage[13:])
                        if lastmessage[0:18] == "OpenWrite::noopen":
                            raise MMASyntaxError(lastmessage[0:18],
                                                 lastmessage[20:])
                    elif messagetype == "P":
                        print(lastmessage)
                    messagefound = False
                    messagelength = 0
                    messagetype = ""
                    lastmessage = ""
                continue
            elif not outputfound and not messagefound:
                if liner[:4] == "Out[":
                    outputfound = True
                    for pos in range(len(liner) - 4):
                        if liner[pos + 4] == ']':
                            mmaexeccount = int(liner[4:(pos + 4)])
                            outputtext = liner[(pos + 7):] + "\n"
                            sangria = pos + 7
                            break
                        continue
                elif liner[:2] == "P:" or liner[:2] == "M:":
                    messagetype = liner[0]
                    messagefound = True
                    k = 2
                    for i in range(len(liner)-2):
                        k = k + 1
                        if liner[i+2] == ":":
                            break
                    messagelength = int(liner[2:(k-1)])
                    lastmessage = lastmessage + liner[k:]
                else:  # For some reason, Information do not pass
                        # through Print or  $PrePrint
                    if liner != "":
                        print(liner)
            else:  # Shouldn't happen
                print("extra line? " + liner)
        if mmaexeccount > 0:
            self.execution_count = mmaexeccount
        return(outputtext)


    def process_response_mathics(self, resp):
        """
        This routine splits the output from messages
        and prints generated before it, and send the corresponding messages.
        It would be better to capture them on the flight, at the very moment
        when the process print them, but it would involve a
        change in the wrapper.
        """
        lineresponse = resp.splitlines()
        outputfound = False
        messagefound = False
        messagetype = None
        messagelength = 0
        lastmessage = ""
        mmaexeccount = -1
        outputtext = "null:"
        sangria = 0
        for linnum, liner in enumerate(lineresponse):
            if linnum == 0:
                liner = liner[1:]
            # self.log.warning(str(linnum) + ": " + liner)
            if outputfound:
                if liner.strip() == "":
                    continue
                if liner[:4] == "Out[":
                    break
                outputtext = outputtext + liner
            elif messagefound:
                lastmessage = lastmessage + "\n" + liner
                if len(lastmessage) >= messagelength:
                    if messagetype == "M":
                        self.show_warning(lastmessage)
                        if msg[:65] == "ToExpression::sntxi: Incomplete expression; more input is needed " or \
                           msg[:48] == "ToExpression::sntx: Invalid syntax in or before ":
                            raise MMASyntaxError("Syntax::sntxi", -1, "sntxi")
                        if lastmessage[0:8] == "Syntax::":
                            for p in range(len(lastmessage)):
                                if lastmessage[p] == ":":
                                    break
                            raise MMASyntaxError(lastmessage[0:p], -1,
                                                 lastmessage[p+1:])
                        if lastmessage[0:11] == "Power::infy":
                            raise MMASyntaxError(lastmessage[0:11],
                                                 lastmessage[13:])
                    elif messagetype == "P":
                        print(lastmessage)
                    messagefound = False
                    messagelength = 0
                    messagetype = ""
                    lastmessage = ""
                continue
            elif not outputfound and not messagefound:
                if liner[:4] == "Out[":
                    outputfound = True
                    for pos in range(len(liner) - 4):
                        if liner[pos + 4] == ']':
                            mmaexeccount = int(liner[4:(pos + 4)])
                            outputtext = liner[(pos + 7):] + "\n"
                            sangria = pos + 7
                            break
                        continue
                elif liner[:2] == "P:" or liner[:2] == "M:":
                    messagetype = liner[0]
                    messagefound = True
                    k = 2
                    for i in range(len(liner)-2):
                        k = k + 1
                        if liner[i+2] == ":":
                            break
                    messagelength = int(liner[2:(k-1)])
                    lastmessage = lastmessage + liner[k:]
                else:  # For some reason, Information do not pass
                        # through Print or  $PrePrint
                    print(liner)
            else:  # Shouldn't happen
                print("extra line? " + liner)

        if mmaexeccount > 0:
            self.execution_count = mmaexeccount
        return(outputtext)


    def postprocess_response(self, outputtext):
        # self.log.warning("*** postprocessing " + outputtext + "...")
        if(outputtext[:5] == 'null:'):
            return None
        if (outputtext[:7] == 'string:'):
            while outputtext[-1] == "\n":
                outputtext = outputtext[:-1]
            outputtext = outputtext[7:].rstrip()
            outputtext = base64.standard_b64decode(outputtext)
            outputtext = outputtext.decode("utf-8")
            return "    " + outputtext
        if (outputtext[:7] == 'mathml:'):
            for p in range(len(outputtext) - 7):
                pp = p + 7
                if outputtext[pp] == ':':
                    lentex = int(outputtext[7:pp])
                    fullformtxt = outputtext[(pp + lentex + 2):]
                    fullformtxt = fullformtxt.replace("\"", "\\\"")
                    htmlstr = outputtext[(pp + 1):(pp + lentex + 1)]
                    htmlstr = "<div onclick='alert(\"" + fullformtxt + "\");'>" + htmlstr + "</div>"
#                    self.Display(HTML(htmlstr))
                    return HTML(htmlstr)
        if (outputtext[:4] == 'tex:'):
            while outputtext[-1] == "\n":
                outputtext = outputtext[:-1]
            outputtext = outputtext[4:].rstrip()
            outputtext = base64.standard_b64decode(outputtext)
            outputtext = outputtext.decode("utf-8")
            # self.log.warning("output latex: " + outputtext)
            for p in range(len(outputtext)):
                if outputtext[p] == ':':
                    lentex = int(outputtext[:p])
                    latexout = Latex('$' + \
                                       outputtext[(p + 1):(p + lentex + 1)] + \
                                       '$')
                    standardout = outputtext[(p + lentex + 2):]
                    return latexout

        if(outputtext[:3] == '3d:'):
            for p in range(len(outputtext) - 31):
                pp = p + 31
                if outputtext[pp] == ':':
                    grstr= """ "<div class=\\"output_area\\"><div class=\\"run_this_cell\\" ></div> <div class=\\"prompt\\" ></div> <div  class=\\"output_subarea output_text output_result\\"><graphics3d  data='"""
                    grstr = grstr + outputtext[31:pp]
                    grstr = grstr + "'/></div></div>" + "\";"
                    jscommands = """
                        requirejs(["nbextensions/nbmathics/static/main"],function(main){require('main');
                        var last3d=$(this)[0].element[0];
                        last3d.innerHTML=last3d.innerHTML+""" + grstr

                    jscommands = jscommands + """
                    last3d = last3d.lastChild.lastChild;
                    var jsondata = atob(last3d.lastChild.getAttribute("data"));
                    jsondata = JSON.parse(jsondata);
                    drawGraphics3D(last3d, jsondata);});
                    """
                    self.Display(Javascript(jscommands))
                    return "    " + outputtext[(pp + 1):]

        if(outputtext[:4] == 'svg:'):
            for p in range(len(outputtext) - 4):
                pp = p + 4
                if outputtext[pp] == ':':
                    self.log.warning(outputtext[(pp+1):])
                    self.Display(Image(outputtext[4:pp]))
                    return outputtext[(pp + 1):]

        if(outputtext[:6] == 'image:'):
            for p in range(len(outputtext) - 6):
                pp = p + 6
                if outputtext[pp] == ':':
                    print(outputtext[6:pp])
                    self.Display(Image(outputtext[6:pp]))
                    return outputtext[(pp + 1):]

        if(outputtext[:4] in ['jpg:', 'png:']):
            for p in range(len(outputtext) - 18):
                pp = p + 18
                if outputtext[pp] == ':':
                    self.Display(HTML(
                        "<center><img class='unconfined' src=\"" +
                        outputtext[4:pp] + "\"></img></center>"))
                    return outputtext[(pp + 1):]

        if(outputtext[:4] == 'wav:'):
            self.Display(Audio(url=outputtext[4:],
                               autoplay=False, embed=True))
            return "-- sound --"

        if(outputtext[:6] == 'sound:'):
            for p in range(len(outputtext) - 6):
                pp = p + 6
                if outputtext[pp] == ':':
                    self.Display(Audio(url=outputtext[6:pp],
                                       autoplay=False, embed=True))
                    return outputtext[(pp + 1):]

    def post_execute(self, retval, code, silent):
        if (retval is not None):
            try:
                data = _formatter(retval, self.repr)
            except Exception as e:
                self.Error(e)
                return
            content = {
                'execution_count': self.execution_count,
                'data': data,
                'metadata': {},
            }
            if not silent:
                if Widget and isinstance(retval, Widget):
                    self.Display(retval)
                    return
                self.send_response(self.iopub_socket,
                                   'execute_result', content)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        resp = self.wrapper.run_command('? %s' % obj, timeout=-1,
                                        stream_handler=None)
        return resp

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        query = "Do[Print[n],{n,Names[\"" + \
                info['obj'] + "*\"]}];$Line=$Line-1;"
        output = self.wrapper.run_command(query, timeout=-1,
                                          stream_handler=None)
        lines = [s.strip() for s in output.splitlines() if s.strip() != ""]
        resp = []
        for l in lines:
            for k in range(len(l)-2):
                if l[k+2] == ":":
                    break
            resp.append(l[k+3:])
        return resp

    def set_variable(self, var, value):
        if not hasattr(self, "kernel_type"):
            return
        # self.log.warning(value)
        if type(value) is str:
            self.do_execute_direct_single_command(var + ' = ' + value,
                                                  envelop=False)
        else:
            self.do_execute_direct_single_command(var +
                                                  ' = "' + value.__repr__() + '"',
                                                  envelop=False)

    def get_variable(self, var):
        res = self.do_execute_direct_single_command(var, evelop=False)
        # self.log.warning(res)
        return res

    def handle_plot_settings(self):
        pass

    def _make_figs(self, plot_dir):
        pass


def _formatter(data, repr_func):
    reprs = {}
    reprs['text/plain'] = repr_func(data)

    lut = [("_repr_png_", "image/png"),
           ("_repr_jpeg_", "image/jpeg"),
           ("_repr_html_", "text/html"),
           ("_repr_markdown_", "text/markdown"),
           ("_repr_svg_", "image/svg+xml"),
           ("_repr_latex_", "text/latex"),
           ("_repr_json_", "application/json"),
           ("_repr_javascript_", "application/javascript"),
           ("_repr_pdf_", "application/pdf")]

    for (attr, mimetype) in lut:
        obj = getattr(data, attr, None)
        if obj:
            reprs[mimetype] = obj

    retval = {}
    for (mimetype, value) in reprs.items():
        try:
            value = value()
        except Exception:
            pass
        if not value:
            continue
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except Exception:
                value = base64.encodestring(value)
                value = value.decode('utf-8')
        try:
            retval[mimetype] = str(value)
        except Exception:
            retval[mimetype] = value
    return retval


if __name__ == '__main__':
    #    from ipykernel.kernelapp import IPKernelApp
    #    IPKernelApp.launch_instance(kernel_class=MathicsKernel)
    WolframKernel.run_as_main()
