
(* ::Package:: *)
BeginPackage["Jupyter`"];
(* Process the output *)
Jupyter`tmpdir = CreateDirectory[]
imagewidth = 500

SetImagesWidth[width_]:=(imagewidth=width)



SetImageOutputFormat[format_]:=If[format=="svg",JupyterReturnImage = JupyterReturnBase64SVG,
                                                JupyterReturnImage = JupyterReturnBase64PNG]


ImageOutputFormat[]:=If[JupyterReturnImage == JupyterReturnBase64SVG,"svg",
                                                "png"]


ImagesWidth[]:=imagewidth

$DisplayFunction=Identity;


(*Internals: Hacks Print and Message to have the proper format*)

Begin["Jupyter`Private`"];


If[StringTake[$Version,{1,7}] == "Mathics", Mathics=True; Print["Running Mathics"]; , Mathics=False;]


JupyterPrePrintFunction[v_]:=WriteString[JupyterSTDOUT,"Out["<>ToString[$Line]<>"]= " <> JupyterReturnValue[v]<>"\n"]

JupyterReturnValue[Null]:="null:"

(*JupyterReturnExpressionTeX[v_]:=( texstr=StringReplace[ToString[TeXForm[v]],"\n"->" "];
			       "tex:"<> ExportString[ToString[StringLength[texstr]]<>":"<> texstr<>":"<>
						  ToString[InputForm[v]], "BASE64"])
*)
JupyterReturnImageFileSVG[v_]:= Module[{ fn = Jupyter`tmpdir <> "/session-figure"<>ToString[$Line]<>".svg"},
				    Export[fn, v, "SVG",ImageSize->Jupyter`imagewidth];
				    "image:" <> fn 			    
				   ]


JupyterReturnImageFileJPG[v_]:= Module[{ fn = Jupyter`tmpdir <> "/session-figure"<>ToString[$Line]<>".jpg"},
				    Export[fn,v,"jpg",ImageSize->Jupyter`imagewidth];
				    "image:" <> fn 			    
				   ]

JupyterReturnImageFilePNG[v_]:= Module[{ fn = Jupyter`tmpdir <> "/session-figure"<>ToString[$Line]<>".png"},
				    Export[fn,v,"png",ImageSize->Jupyter`imagewidth];
				    "image:" <> fn 			    
				   ]

JupyterReturnBase64SVG[v_]:= "svg:" <> "data:image/svg+xml;base64," <> 
                                  StringReplace[ExportString[ExportString[v,"SVG", ImageSize->Jupyter`imagewidth],"Base64"],"\n"->""]

JupyterReturnBase64JPG[v_]:= "jpg:" <> "data:image/jpg;base64," <> 
                                  StringReplace[ExportString[ExportString[v,"jpg", ImageSize->Jupyter`imagewidth],"Base64"],"\n"->""]

JupyterReturnBase64PNG[v_]:= "png:" <> "data:image/png;base64," <> 
                                  StringReplace[ExportString[ExportString[v,"png", ImageSize->Jupyter`imagewidth],"Base64"],"\n"->""]


JupyterReturnValue[v_Graphics]:= JupyterReturnImage[v]  <>  ":" <> "- graphics -"

JupyterReturnValue[v_Graphics3D]:= JupyterReturnImage[v]  <>  ":" <> "- graphics3D -"



JupyterReturnValue[v_]:= If[And[FreeQ[v,Graphics],FreeQ[v,Graphics3D]], 
			    JupyterReturnExpressionTeX[v],
			    (*else*)
			    JupyterReturnImage[v] <> ":" <>
			    ToString[InputForm[#1/.{Graphics[___]-> "- graphics -",
						    Graphics3D[___]-> "- graphics3D -"}]]
			   ]



JupyterReturnValue[v_Sound]:= "wav:"<> "data:audio/wav;base64," <> ExportString[ExportString[v,"wav"],"Base64"]

(*Definitions depending on the platform*)
If[StringTake[$Version,{1,7}] == "Mathics", 
   (*Print["Defining system dependent expressions for mathics"];*)
   (*   JupyterReturnImage = JupyterReturnImageFileSVG; *)
   JupyterReturnImage = JupyterReturnBase64SVG; 
   JupyterReturnValue[v_String]:= "string:"<> ExportString[v, "Base64"];   
   JupyterReturnExpressionTeX[v_]:=( texstr=StringReplace[ToString[TeXForm[v]],"\n"->" "];
				     "tex:"<> ExportString[ToString[StringLength[texstr]]<>":"<> texstr<>":"<>
							   ToString[InputForm[v]] , "Base64"]);
   JupyterSTDOUT = OutputStream["stdout", 1];
   ,(*Else*)
   (* Print["Defining system dependent expressions for mma "];*)
   (* JupyterReturnImage = JupyterReturnImageFilePNG; *)
   JupyterReturnImage = JupyterReturnBase64PNG; 
   JupyterReturnValue[v_String]:= "string:"<>ExportString[v,"Base64"];
   JupyterReturnExpressionTeX[v_]:=( texstr=StringReplace[ToString[TeXForm[v]],"\n"->" "];
			       "tex:"<> ExportString[ToString[StringLength[texstr]]<>":"<> texstr<>":"<>
						  ToString[InputForm[v]], "Base64"]);   
   JupyterSTDOUT = OutputStream["stdout", 1];
  ]





JupyterMessage[m_MessageName, vars___] :=
  WriteString[OutputStream["stdout", 1], BuildMessage[m, vars]];
BuildMessage[something___] := "";
BuildMessage[$Off[], vals___] := "";
BuildMessage[m_MessageName, vals___] := Module[{lvals, msgs, msg},
					       lvals = List@vals;
					       lvals = ToString[#1, InputForm] & /@ lvals;
					       lvals = Sequence @@ lvals;
					       msgs = Messages[m[[1]] // Evaluate];
							       If[Length[msgs] == 0, Return[""]];
							       msg = m /. msgs;
							       msg = ToString[m]<>": "<>ToString[StringForm[msg, lvals]];
							       msg = "\nM:" <> ToString[StringLength[msg]] <> ":" <> msg <> "\n"
							       ];

(*Redefine Preprint Function*)
System`$PrePrint:=JupyterPrePrintFunction
(*Redefine Message*)
Unprotect[Message];
Message[m_MessageName, vals___] :=
WriteString[OutputStream["stdout", 1], BuildMessage[m, vals]];
Unprotect[Message];

(*Redefine Print*)
 Unprotect[Print];
 Print[s_] := WriteString[OutputStream["stdout", 1],  
"P:" <> ToString[StringLength[ToString[s]]] <> ":" <> ToString[s]<>"\n\n"]
 Protect[Print];
End[];
EndPackage[];

