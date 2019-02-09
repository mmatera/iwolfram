# iwolfram

Jupyter Interface for Wolfram Mathematica / Mathics Notebooks based on Metakernel. The idea is to have a common kernel for both versions of the language with a compatible notebook form.

By now is just a proof of concept.


Contributing
------------

Please feel encouraged to contribute to this project! Create your own fork, make the desired changes, commit, and make a pull request.

[![Build Status](https://travis-ci.org/mmatera/iwolfram.svg?branch=master)](https://travis-ci.org/mmatera/iwolfram)

License
-------

IWolfram is released under the GNU General Public License (GPL).

Interactive 3D Graphics
-----------------------

A basic support for interactive 3D graphics is implemented. The implementation is based on Three.js and the interface developed by Angus Griffith for the Mathics Project (https://github.com/mathics/Mathics).

About graphics
---------------

Currently, iwolfram has almost full supports for graphics when uses the original Wolfram's Mathematica kernel as the backend, and a very limited support when runs over the Mathics kernel. On the other hand, to generate image files, Wolfram's requires that the user have a graphic terminal open on the server. Worst, if a graphic server is not available, a call to a graphic command make the iwolfram kernel to crash.  If we run the jupyter server in the same machine we are running the front end this is not a problem, but it could be if the server runs in a remote machine. To overcome this issue, a workaround is to use the xvfb xorg kernel to simulate a graphic server. To do this, we need to install xvfb in the computer where jupyter is going to run, and establish 

'xvfb-run -a -s "-screen 0 640x480x24"  [path to the mma kernel executable]/MathKernel'
 
 as the the kernel backend. 


