
(* ::Package:: *)
BeginPackage["Jupyter`"];
(* Process the output *)
Jupyter`tmpdir = CreateDirectory[]
imagewidth = 500

SetImagesWidth[width_]:=imagewidth = 500

ImagesWidth[]:=imagewidth

$DisplayFunction=Identity;


(*Internals: Hacks Print and Message to have the proper format*)
Begin["Private`"];

JupyterPrePrintFunction[v_]:=WriteString[OutputStream["stdout", 1],"Out["<>ToString[$Line]<>"]= " <> JupyterReturnValue[v]<>"\n"]

System`$PrePrint:=JupyterPrePrintFunction

JupyterReturnValue[Null]:="null:"

JupyterReturnValue[v_]:= Module[{fn},
			 If[And[FreeQ[v,Graphics],FreeQ[v,Graphics3D]], 
			    texstr=StringReplace[ToString[TeXForm[v]],"\n"->" "];
			    "tex:"<> ExportString[ToString[StringLength[texstr]]<>":"<> texstr<>":"<>
						  ToString[InputForm[v]], "BASE64"],
			    (*else*)
			    fn = Jupyter`tmpdir <> "/session-figure"<>ToString[$Line]<>".jpg";
			    Export[fn,v,"jpg",ImageSize->Jupyter`imagewidth];
			    "image:"<>fn<>":"<>ToString[InputForm[#1/.{Graphics[___]-> "--graphics--",
								       Graphics3D[___]-> "--graphics3D--"}]]
                               ]
			   ]


JupyterReturnValue[v_String]:= "string:"<>ExportString[v,"BASE64"]

JupyterReturnValue[v_Sound]:=Module[{fn=Jupyter`tmpdir <> "/session-sound"<>ToString[$Line]<>".wav"},
			     Export[fn,v,"wav"];
			     "sound:"<>fn<>":"<>"- sound -"]


JupyterReturnValue[v_Graphics]:=Module[{fn=Jupyter`tmpdir <> "/session-sound"<>ToString[$Line]<>".jpg"},
			    Export[fn,v,"jpg", ImageSize->Jupyter`imagewidth];
			    "image:"<>fn<>":"<>"- graphics -"]


JupyterReturnValue[v_Graphics3D]:=Module[{fn=Jupyter`tmpdir <> "/session-sound"<>ToString[$Line]<>".jpg"},
			    Export[fn,v,"jpg", ImageSize->Jupyter`imagewidth];
			    "image:"<>fn<>":"<>"- graphics -"]

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
(*Redefine Message*)
Unprotect[Message];
Message[m_MessageName, vals___] :=
WriteString[OutputStream["stdout", 1], BuildMessage[m, vals]];
Unprotect[Message];

(*Redefine Print*)
 Unprotect[Print];
 Print[s_] := WriteString[OutputStream["stdout", 1],  "
P:" <> ToString[StringLength[ToString[s]]] <> ":" <> ToString[s]<>"\n\n"]
 Protect[Print];
End[];
EndPackage[];

