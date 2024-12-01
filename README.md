# IWolfram

Jupyter Interface for Wolfram Mathematica / Mathics Notebooks
based on [Metakernel](https://github.com/Calysto/metakernel).
The idea is to have a common kernel for both versions of the
language with a compatible notebook form.

So far this is a proof of concept.

Installing
----------

```
$ pip install -e .
...
Installing collected packages: wolfram-kernel
Running setup.py develop for wolfram-kernel
Successfully installed wolfram-kernel
```

Running
-------

Launch by running this command in a terminal
```
$ jupyter notebook --kernel=wolfram_kernel
```

This will launch the Jupyter file explorer in a browser window.
Navigate to the `examples` folder and open the example worksheet
called `Examples and tests.ipynb`.

Contributing
------------

Please feel encouraged to contribute to this project! Create your
own fork, make the desired changes, commit, and make a pull request.

[![Build Status](https://travis-ci.org/mmatera/iwolfram.svg?branch=master)](https://travis-ci.org/mmatera/iwolfram)

License
-------

IWolfram is released under the GNU General Public License (GPL).

Interactive 3D Graphics
-----------------------

Basic support for interactive 3D graphics is implemented. The implementation
is based on [Three.js](https://threejs.org) and on the interface developed by
Angus Griffith for [the Mathics Project](https://github.com/mathics/Mathics).

About graphics
---------------

Currently, IWolfram has almost full support for graphics when using the
original Wolfram Mathematica as the backend, and a very limited support
when using Mathics. On the other hand, to generate image files, Wolfram
Mathematica requires that the user have a graphic terminal open on the
server. Worse, if a graphic server is not available, any call to a graphic
command crashes the IWolfram kernel. If we run the Jupyter Notebook server
on the same machine we are running the front end this is not a problem,
but it can be if the server runs in a remote machine. To overcome this
issue, a workaround is to use
[the Xvfb xorg kernel](https://www.x.org/releases/X11R7.7/doc/man/man1/Xvfb.1.xhtml)
to simulate a graphic server. To do this, we need to install Xvfb on the
computer where the Jupyter Notebook server will run, and to set
```
xvfb-run -a -s "-screen 0 640x480x24" <path_to_the_mma_kernel_executable>/MathKernel
```
as the the kernel backend invocation command.

