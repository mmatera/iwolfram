
(* ::Package:: *)
BeginPackage["Jupyter`"];
(* Process the output *)
Jupyter`tmpdir = CreateDirectory[]
imagewidth = 500
$PrePrint:=Module[{fn,res,texstr},
		  If[#1 === Null, res="null:",
		     Switch[Head[#1],
			    String,
			    res="string:"<>ExportString[#1,"BASE64"],
			    Graphics,
			    fn=Jupyter`tmpdir <> "/session-figure"<>ToString[$Line]<>".jpg";
			    Export[fn,#1,"jpg", ImageSize->Jupyter`imagewidth];
			    res="image:"<>fn<>":"<>"- graphics -",
			    Graphics3D,
			    fn=Jupyter`tmpdir <> "/session-figure"<>ToString[$Line]<>".jpg";
			    Export[fn,#1,"jpg", ImageSize->Jupyter`imagewidth];
			    res="image:"<>fn<>":"<>"- graphics3d -",
			    Sound,
			    fn=Jupyter`tmpdir <> "/session-sound"<>ToString[$Line]<>".wav";
			    Export[fn,#1,"wav"];
			    res="sound:"<>fn<>":"<>"- sound -",
			    _,
                            If[And[FreeQ[#1,Graphics],FreeQ[#1,Graphics3D]], 
			         texstr=StringReplace[ToString[TeXForm[#1]],"
"->" "];
			         res="tex:"<> ExportString[ToString[StringLength[texstr]]<>":"<> texstr<>":"<>ToString[InputForm[#1]], "BASE64"],
                               (*else*)
    			         fn = Jupyter`tmpdir <> "/session-figure"<>ToString[$Line]<>".jpg";
			         Export[fn,#1,"jpg",ImageSize->Jupyter`imagewidth];
			         res="image:"<>fn<>":"<>ToString[InputForm[#1/.{Graphics[___]-> "--graphics--",Graphics3D[___]-> "--graphics3D--"}]]
                               ]
			   ]
		     ];
		  WriteString[OutputStream["stdout", 1],"Out["<>ToString[$Line]<>"]= " <> res<>"\n"];
		  ""
		  ]&;
$DisplayFunction=Identity;

(*Internals: Hacks Print and Message to have the proper format*)
Begin["Private`"];
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
							       msg = "
M:" <> ToString[StringLength[msg]] <> ":" <> msg <> "
"
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

