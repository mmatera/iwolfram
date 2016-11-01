from __future__ import print_function

from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper,u
from metakernel.process_metakernel import TextOutput
from metakernel.pexpect import EOF

from IPython.display import Image, SVG
from IPython.display import Latex, HTML, Javascript
from IPython.display import Audio

import subprocess
import os
import sys
import tempfile

import base64

__version__ = '0.0.0'

try:
    from .config import mathexec
except Exception:
    mathexec = "mathics"

class MMASyntaxError(BaseException):
    def __init__(self,val=0,name="",traceback=None):
        self.val=val
        self.name=name
        self.traceback=traceback

        

class WolframKernel(ProcessMetaKernel):
    implementation = 'Wolfram Mathematica Kernel'
    implementation_version = __version__,
    language = 'mathematica'
    language_version = '10.0',
    banner = "Wolfram Mathematica Kernel"
    language_info = {
        'exec': mathexec,
        'mimetype': 'text/x-mathics',
        'name': 'wolfram_kernel',
        'file_extension': '.m',
        'help_links': MetaKernel.help_links,
    }

    kernel_json = {
        'argv': [ sys.executable, '-m', 'wolfram_kernel', '-f', '{connection_file}'],
        'display_name': 'Wolfram Mathematica',
        'language': 'mathematica',
        'name': 'wolfram_kernel'
    }
    def get_usage(self):
        return "This is the Wolfram Mathematica kernel."

    def repr(self, data):
        return data

    _initstringwolfram = """
(* ::Package:: *)
BeginPackage[\"Jupyter`\"];
(* Process the output *)
Unprotect[System`OutputSizeLimit];
System`$OutputSizeLimit=Infinity;
Protect[System`OutputSizeLimit];
imagewidth = 500
$PrePrint:=Module[{fn,res,texstr},
		  If[#1 === Null, res=\"null:\",
		     Switch[Head[#1],
			    String,
			    res=\"string:\"<>ExportString[#1,\"BASE64\"],
			    Graphics,
			    fn=\"{sessiondir}/session-figure\"<>ToString[$Line]<>\".jpg\";
			    Export[fn,#1,\"jpg\", ImageSize->Jupyter`imagewidth];
			    res=\"image:\"<>fn<>\":\"<>\"- graphics -\",
			    Graphics3D,
			    fn=\"{sessiondir}/session-figure\"<>ToString[$Line]<>\".jpg\";
			    Export[fn,#1,\"jpg\", ImageSize->Jupyter`imagewidth];
			    res=\"image:\"<>fn<>\":\"<>\"- graphics3d -\",
			    Sound,
			    fn=\"{sessiondir}/session-sound\"<>ToString[$Line]<>\".wav\";
			    Export[fn,#1,\"wav\"];
			    res=\"sound:\"<>fn<>\":\"<>\"- sound -\",
			    _,
                            If[And[FreeQ[#1,Graphics],FreeQ[#1,Graphics3D]], 
			         texstr=StringReplace[ToString[TeXForm[#1]],\"\n\"->\" \"];
			         res=\"tex:\"<> ExportString[ToString[StringLength[texstr]]<>\":\"<> texstr<>\":\"<>ToString[InputForm[#1]], \"BASE64\"],
                               (*else*)
    			         fn=\"{sessiondir}/session-figure\"<>ToString[$Line]<>\".jpg\";
			         Export[fn,#1,\"jpg\",ImageSize->Jupyter`imagewidth];
			         res=\"image:\"<>fn<>\":\"<>ToString[InputForm[#1/.{Graphics[___]-> \"--graphics--\",Graphics3D[___]-> \"--graphics3D--\"}]]
                               ]
			   ]
		     ];
		  res
		  ]&;
$DisplayFunction=Identity;

(*Internals: Hacks Print and Message to have the proper format*)
Begin[\"Private`\"];
JupyterMessage[m_MessageName, vars___] :=
  WriteString[OutputStream[\"stdout\", 1], BuildMessage[m, vars]];
BuildMessage[something___] := \"\";
BuildMessage[$Off[], vals___] := \"\";
BuildMessage[m_MessageName, vals___] := Module[{lvals, msgs, msg},
					       lvals = List@vals;
					       lvals = ToString[#1, InputForm] & /@ lvals;
					       lvals = Sequence @@ lvals;
					       msgs = Messages[m[[1]] // Evaluate];
							       If[Length[msgs] == 0, Return[\"\"]];
							       msg = m /. msgs;
							       msg = ToString[m]<>": "<>ToString[StringForm[msg, lvals]];
							       msg = \"\nM:\" <> ToString[StringLength[msg]] <> \":\" <> msg <> \"\n\"
							       ];
(*Redefine Message*)
Unprotect[Message];
Message[m_MessageName, vals___] :=
WriteString[OutputStream[\"stdout\", 1], BuildMessage[m, vals]];
Unprotect[Message];

(*Redefine Print*)
 Unprotect[Print];
 Print[s_] := WriteString[OutputStream[\"stdout\", 1],  \"\nP:\" <> ToString[StringLength[ToString[s]]] <> \":\" <> ToString[s]<>\"\\n\\n\"]
 Protect[Print];
End[];
EndPackage[];

"""


    _initstringmathics = """
System`$OutputSizeLimit=1000000000000
$PrePrint:=Module[{fn,res,mathmlstr}, 
If[#1 === Null, res=\"null:\",

Switch[Head[#1],
          String,
            res=\"string:\"<>#1,
          _,            
            mathmlstr=ToString[MathMLForm[#1]];
            res=\"mathml:\"<>ToString[StringLength[mathmlstr]]<>\":\"<> mathmlstr<>\":\"<>ToString[InputForm[#1]]
       ]
       ];
       res
    ]&;
$DisplayFunction=Identity;
"""

    _session_dir = ""
    _first = True
    initfilename = ""
    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            banner = "mathics 0.1"
            self._banner = u(banner)
        return self._banner

    def check_wolfram(self):
        starttext = os.popen("bash -c 'echo |" +  self.language_info['exec']  +"'").read()
        if starttext[:11] == "Mathematica":			      
            self.is_wolfram = True
        else:
            self.is_wolfram = False
        return self.is_wolfram

    def __init__(self,*args, **kwargs):
        super(WolframKernel,self).__init__(*args,**kwargs)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        self.log.warning("help required")
        if none_on_fail:
            return None
        else:
            return "Sorry, no help is available on '%s'." % info['code']


    def show_warning(self, warning):
        self.send_response(self.iopub_socket, 'stream',
                           {'wait': True, 'name': "stderr", 'text': warning} )
        return

    def print(self, msg):
        self.send_response(self.iopub_socket, 'stream',
                           {'wait': True, 'name': "stdout", 'text': msg+"\n"} )
        return

        
    def build_initfile(self):
        if self.is_wolfram:
            self._initstring = self._initstringwolfram
        else:
            self._initstring = self._initstringmathics
        self._first = True
        self._session_dir = tempfile.mkdtemp()
        self._initstring = self._initstring.replace("{sessiondir}", self._session_dir)
        self.initfilename = self._session_dir + '/init.m'
        print(self.initfilename)
        f = open(self.initfilename, 'w')
        f.write(self._initstring)
        f.close()
        

    def makeWrapper(self):
        """
	Start a math/mathics kernel and return a :class:`REPLWrapper` object.
        """
        self.js_libraries_loaded = False
        orig_prompt = u('In\[.*\]:=')  # Maybe we can consider as prompt P:, M: and Out[]:= to catch all signals in real time
        prompt_cmd = None
        change_prompt = None
        self.check_wolfram()
        self.build_initfile()
        
        if not self.is_wolfram:
            cmdline = self.language_info['exec'] + " --colors NOCOLOR --persist '" +  self.initfilename + "'"
        else:
            cmdline = self.language_info['exec'] + " -initfile '"+ self.initfilename+"'"
        replwrapper = REPLWrapper(cmdline, orig_prompt, change_prompt,
                                  prompt_emit_cmd = None, echo=True)
        return replwrapper

    def check_js_libraries_loaded(self):
        if self.js_libraries_loaded:
            return
        jscode="""
           if(document.getElementById("graphics3dScript") == null){
               var tagg = document.createElement('script');
               tagg.type = "text/javascript";
               tagg.src = "/static/js/graphics3d.js";
               tagg.charset = 'utf-8';
               tagg.id = "graphics3dScript"
               document.getElementsByTagName("head")[0].appendChild( tagg );
               alert("library loaded");
          }else{alert("library was loaded before");}
        """
        self.Display(Javascript(jscode))        
        self.js_libraries_loaded = True



    def do_execute_direct_single_command(self, code, stream_handler=None):
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
        try:
            output = self.wrapper.run_command(code.rstrip(), timeout=-1,
                                     stream_handler=stream_handler)
# TODO:  instead of proccess_response, it would be better to capture the prints and warnings at the moment they are sended.
            output = self.process_response(output)
            if stream_handler is not None:
                output = ''

        except MMASyntaxError as e:
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




    def update_bracket_string(self, bracketstring, codeline):
        escape = False
        codeline = codeline.strip()
        if codeline == "" :
            return bracketstring
        
        string_open = bracketstring != "" and bracketstring[-1] == '"'
 
        if  not string_open and  bracketstring != "" and  bracketstring[-1] in ['+','-','*','/','>','<','=','^',',']:    
            bracketstring = bracketstring[:-1]

        for c in codeline:
            if string_open:
                if escape:
                    escape = False
                elif c == "\\" and string_open:
                    escape = True
                elif c == '"':
                    string_open = False
                    bracketstring = bracketstring[:-1]
                continue
            if c == '"':
                string_open = True
                bracketstring = bracketstring +  '"'
                continue
            if c in ['(','[','{']:
                bracketstring = bracketstring + c
            if c == ')':
                if bracketstring == "":
                    raise MMASyntaxError("Syntax::sntxf",-1,codeline)                    
                if bracketstring[-1] == '(':
                    bracketstring = bracketstring[:-1]
                else:
                    raise MMASyntaxError("Syntax::sntxf",-1,codeline)                    
            if c == ']':
                if bracketstring == "":
                    raise MMASyntaxError("Syntax::sntxf",-1,codeline)                    
                if bracketstring[-1] == '[':
                    bracketstring = bracketstring[:-1]
                else:
                    raise MMASyntaxError("Syntax::sntxf",-1,codeline)                    
            if c == '}':
                if bracketstring == "":
                    raise MMASyntaxError("Syntax::sntxf",-1,codeline)                    
                if bracketstring[-1] == '{':
                    bracketstring = bracketstring[:-1]
                else:
                    raise MMASyntaxError("Syntax::sntxf",-1,codeline)                    
        if  codeline[-1] in ['+','-','*','/','>','<','=','^',','] and not string_open:    
            bracketstring = bracketstring + codeline[-1]
        return bracketstring
        





    def do_execute_direct(self, code):
        """
        If code is a single line, execute it and postprocess it. For a multiline code, 
        it splits it and call for each line do_execute_direct_single_line(). For all
        except the last codeline, it calls to MetaKernel.post_execute() to send the 
        output to the Kernel. For the last codeline, it leaves thist task to Metakernel.
        """
        # self.check_js_libraries_loaded()
        # Processing multiline code
        codelines =  [codeline.strip() for codeline in  code.splitlines()]
        lastline = ""
        prevcmd = ""
        resp = None

        bracketstring = ""
        for codeline in codelines:
            try:
                bracketstring = self.update_bracket_string(bracketstring,codeline)
                if bracketstring != "" and bracketstring[-1] == '"':
                    codeline = codeline + "\\n"
            except MMASyntaxError as e:
                self.kernel_resp = {
                    'status': 'error',
                    'execution_count': self.execution_count,
                    'ename': e.name, 'evalue': e.val,
                    'traceback': e.traceback,
                }
                return
            # If brackets are not balanced, add codeline to lastline and continue
            if bracketstring != "":
                lastline = lastline + codeline 
                continue
            # If brackets are balanced, and the new line is empty:
            if codeline == "":
                if lastline == "":
                    continue
                # If there was a resp before, calls post_execute and continue. This have to be here because for the last line,
                # post_execute is called directly from the main loop of  MetaKernel
                if not resp is None :
                    # print(resp)
                    self.post_execute(resp, prevcmd, False)
                resp = self.do_execute_direct_single_command(lastline)
                resp = self.postprocess_response(resp.output)
                prevcmd = lastline
                lastline = ""
                continue
            lastline = lastline + codeline

        # Finishing to process the line before the last line
        if lastline == "":
            return resp
        else:
            if not resp  is None :
                self.post_execute(resp, prevcmd, False)

        # If the last line is complete: 
        if bracketstring != "":
            if bracketstring[-1] in ['(','[','{']:
                errname = "Syntax::bktmcp"
                self.show_warning("Syntax::bktmcp: Expression has no closing" + bracketstring[-1])
            else:
                errname = "Syntax::tsntxi"
                self.show_warning("Syntax::bktmcp: Expression incomplete.")
            self.kernel_resp = {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': errname, 'evalue': "-1",
                'traceback': lastline,
            }
            return 

        # Evaluating last valid code line
        ##
        ## TODO: Implement the functionality of PrePrint in mathics. It would fix also the call for %# as part of expressions.
        ##
        if not self.is_wolfram:        
            lastline = "$PrePrint[" + lastline + "]"


        resp =  self.do_execute_direct_single_command(lastline)
        return self.postprocess_response(resp.output)


    
    def process_response(self, resp):
        """
        This routine splits the output from messages and prints generated before it, and send the corresponding messages.
        It would be better to capture them on the flight, at the very moment when the process print them, but it would involve a 
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
        self.log.warning("resp:\n-----\n"+resp)
        if self.is_wolfram:
            self.log.warning("lines:")
            for linnum, liner in enumerate(lineresponse):
                self.log.warning("<<" + liner + ">>")
                if outputfound:
                    if liner.strip() == '':
                        if outputtext[-2] == '\\':  
                            outputtext = outputtext[:-2]
                            lineresponse[linnum + 1] = lineresponse[linnum + 1][sangria+4:]
                            addlinebreak = False
                            continue
                    outputtext = outputtext  + liner
                elif messagefound:
                    lastmessage = lastmessage + "\n" + liner
                    if len(lastmessage) >= messagelength:
                        if messagetype == "M":
                            self.show_warning(lastmessage)
                            if lastmessage[0:8] == "Syntax::":
                                for p in range(len(lastmessage)):
                                    if lastmessage[p] == ":":
                                        break
                                raise MMASyntaxError(lastmessage[0:p],-1,lastmessage[p+1:])
                            if lastmessage[0:11] == "Power::infy":
                                raise MMASyntaxError(lastmessage[0:11],lastmessage[13:])
                        elif messagetype == "P":
                            self.print(lastmessage)                            
                        messagefound = False
                        messagelength = 0
                        messagetype = ""
                        lastmessage = ""
                    continue
                elif not outputfound and not messagefound  :
                    if liner[:4] == "Out[":
                        outputfound = True
                        for pos in range(len(liner) - 4):
                            if liner[pos + 4] == ']':
                                mmaexeccount = int(liner[4:(pos + 4)]) 
                                outputtext = liner[(pos + 7):] + "\n"
                                sangria = pos + 7
                                break
                            continue
                    if liner[:2] == "P:" or liner[:2] == "M:":
                        messagetype = liner[0]
                        messagefound = True
                        k = 2
                        for i in range(len(liner)-2):
                            k = k + 1
                            if liner[i+2] == ":":
                                break
                        messagelength = int(liner[2:(k-1)])
                        lastmessage = lastmessage + liner[k:]
                else: #Shouldn't happen
                    self.print("extra line? " + liner)
        else:
            for linnum, liner in enumerate(lineresponse):
                if not outputfound and liner[:4] == "Out[":
                    outputfound = True
                    for pos in range(len(liner) - 4):
                        if liner[pos + 4] == ']':
                            mmaexeccount = int(liner[4:(pos + 4)]) 
                            outputtext = liner[(pos + 7):]
                            break
                        continue
                elif outputfound:
                    if liner == u' ':
                        if outputtext[-1] == '\\':  # and lineresponse[linnum + 1] == '>':
                            outputtext = outputtext[:-1]
                            lineresponse[linnum + 1] = lineresponse[linnum + 1][0] = " "
                            continue
                    outputtext = outputtext + liner[7:]
                else:
                    print(liner)

        if  mmaexeccount>0:
            self.execution_count = mmaexeccount
        
        return(outputtext)


    def postprocess_response(self, outputtext):        
        if(outputtext[:5] == 'null:'):
            return None
        if (outputtext[:7] == 'string:'):
            outputtext = base64.standard_b64decode(outputtext[7:]).decode("utf-8") 
            self.log.warning("clean string:"+outputtext)
            return "    " + outputtext
        if (outputtext[:7] == 'mathml:'):
            for p in range(len(outputtext) - 7):
                pp = p + 7
                if outputtext[pp] == ':':
                    lentex = int(outputtext[7:pp])
                    fullformtxt = outputtext[(pp + lentex + 2):].replace("\"","\\\"")
                    htmlstr = outputtext[(pp + 1):(pp + lentex + 1)]                    
                    htmlstr = "<div onclick='alert(\"" +  fullformtxt   +"\");'>" + htmlstr + "</div>"
#                    self.Display(HTML(htmlstr))
                    return HTML(htmlstr)
        if (outputtext[:4] == 'tex:'):
            self.log.warning("base64 input:"+outputtext[4:])
            outputtext = "    " + base64.standard_b64decode(outputtext[4:]).decode("utf-8") 
            self.log.warning("clean text:"+ outputtext)
            for p in range(len(outputtext) - 4):
                pp = p + 4
                if outputtext[pp] == ':':
                    lentex = int(outputtext[4:pp])
                    self.Display(Latex('$' + outputtext[(pp + 1):(pp + lentex + 1)] + '$'))
                    return outputtext[(pp + lentex + 2):]

        if(outputtext[:4] == 'svg:'):
            for p in range(len(outputtext) - 4):
                pp = p + 4
                if outputtext[pp] == ':':
                    self.Display(SVG(outputtext[4:pp]))
                    return outputtext[(pp + 1):]

        if(outputtext[:6] == 'image:'):
            for p in range(len(outputtext) - 6):
                pp = p + 6
                if outputtext[pp] == ':':
                    print(outputtext[6:pp])
                    self.Display(Image(outputtext[6:pp]))
                    return outputtext[(pp + 1):]
        if(outputtext[:6] == 'sound:'):
            for p in range(len(outputtext) - 6):
                pp = p + 6
                if outputtext[pp] == ':':
                    self.Display(Audio(url=outputtext[6:pp], autoplay=False, embed=True))
                    return outputtext[(pp + 1):]


    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        resp = self.do_execute_direct('? %s' % obj)
        return resp

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        query = "Do[Print[n],{n,Names[\"" + info['obj']  + "*\"]}];$Line=$Line-1;"
        output = self.wrapper.run_command(query, timeout=-1,
                                          stream_handler=None)
        lines = [s for s in output.splitlines() if s != ""]
        resp = []
        for l in lines:
            for k in range(len(l)-2):
                if l[k+2] == ":":
                    break
            resp.append(l[k+3:])
        return resp

    def handle_plot_settings(self):
        pass

    def _make_figs(self, plot_dir):
        pass

if __name__ == '__main__':
#    from ipykernel.kernelapp import IPKernelApp
#    IPKernelApp.launch_instance(kernel_class=MathicsKernel)
    WolframKernel.run_as_main()
