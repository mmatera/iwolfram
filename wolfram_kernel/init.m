
(* ::Package:: *)
BeginPackage["Jupyter`"];
(* Process the output *)
  System`$OutputSizeLimit=Infinity;
$PrePrint:=Module[{fn,res,texstr},
		  If[#1 === Null, res="null:",
		     Switch[Head[#1],
			    String,
			    res="string:"<>#1,
			    Graphics,
			    fn="/tmp/tmprpgt8fkv/session-figure"<>ToString[$Line]<>".png";
			    Export[fn,#1,"png"];
			    res="image:"<>fn<>":"<>"- graphics -",
			    Graphics3D,
			    fn="/tmp/tmprpgt8fkv/session-figure"<>ToString[$Line]<>".png";
			    Export[fn,#1,"png"];
			    res="image:"<>fn<>":"<>"- graphics3d -",
			    Sound,
			    fn="/tmp/tmprpgt8fkv/session-sound"<>ToString[$Line]<>".wav";
			    Export[fn,#1,"wav"];
			    res="sound:"<>fn<>":"<>"- sound -",
			    _,
			    texstr=StringReplace[ToString[TeXForm[#1]],"
"->" "];
			    res="tex:"<>ToString[StringLength[texstr]]<>":"<> texstr<>":"<>ToString[InputForm[#1]]
			    ]
		     ];
		  res
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
P:" <> ToString[StringLength[s]] <> ":" <> s<>"\n\n"]
 Protect[Print];
End[];
EndPackage[];

