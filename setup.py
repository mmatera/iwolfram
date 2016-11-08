from __future__ import print_function

import os, sys
from distutils.core import setup
from setuptools.command.install import install
from distutils import log
from IPython.utils.tempdir import TemporaryDirectory


import json
import os
import sys

try:
    from jupyter_client.kernelspec import install_kernel_spec
except ImportError:
    from IPython.kernel.kernelspec import install_kernel_spec


def subdirs(root, file='*.*', depth=10):
    for k in range(depth):
        yield root + '*/' * k + file


# Reads the specific command line arguments
   
if "--help" in sys.argv:
    print('setup install|build --mma-exec <path to mathematica executable> --iwolfram-mathkernel-path <path to store the caller>')

wmmexec = 'mathics'
wmmcaller = None
if "--mma-exec" in sys.argv:
    idx = sys.argv.index("--mma-exec")
    sys.argv.pop(idx)
    wmmexec = sys.argv.pop(idx) 

# if "--iwolfram-mathkernel-path" in sys.argv:
#     idx = sys.argv.index("--iwolfram-mathkernel-path")
#     sys.argv.pop(idx)
#     wmmcaller = sys.argv.pop(idx) 





class install_with_kernelspec(install):
    def run(self):
        # global wmmcaller
        global wmmexec
        # Determine if the executable is Wolfram Mathematica or mathics
        # starttext = os.popen("bash -c 'echo |" +  wmmexec  +"'").read()
        # if starttext[:11] == "Mathematica":
        #     wmmcaller =  wmmexec
            # if wmmcaller is None:
            #     wmmcaller = '/usr/local/bin/iwolframcaller.sh'
            # with open(wmmcaller,'w') as f:
            #     f.write("#!/bin/sh\n\n")
            #     f.write("# sh envelopment for the true math command ")
            #     f.write("necesary to avoid the kernel hangs on jupyterhub\n\n\n ")
            #     f.write(wmmexec + " $@")
            # os.chmod(wmmcaller, 0o755)
        # else:
        #     wmmcaller = wmmexec

        # Build the configuration file
        configfilestr = "# iwolfram configuration file\nmathexec = '{wolfram-caller-script-path}'\n\n"
        configfilestr = configfilestr.replace('{wolfram-caller-script-path}',wmmexec)
        with open('wolfram_kernel/config.py','w') as f:
            f.write(configfilestr)

        #Run the standard intallation
        install.run(self)

        print("Installing kernel spec")        

        #Build and Install the kernelspec
        from wolfram_kernel.wolfram_kernel import WolframKernel
        kernel_json = WolframKernel.kernel_json        
        with TemporaryDirectory() as td:        
            os.chmod(td, 0o755)  # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            
            log.info('Installing kernel spec')            
            #install_kernel_resources(td,files=['logo-64x64.png'])
            kernel_name = kernel_json['name']
            try:
                install_kernel_spec(td, kernel_name, user=self.user,
                                replace=True)
            except:
                install_kernel_spec(td, kernel_name, user=not self.user,
                                replace=True)


setup(name='wolfram_kernel',
      version='0.11.3',
      description='A Wolfram Mathematica/mathics kernel for Jupyter/IPython',
      long_description='A Wolfram Mathematica/mathics kernel for Jupyter/IPython, based on MetaKernel',
      url='https://github.com/matera/iwolfram/tree/master/iwolfram',
      author='Juan Mauricio Matera',
      author_email='matera@fisica.unlp.edu.ar',
      packages=['wolfram_kernel','wolfram_kernel.web'],
      cmdclass={'install': install_with_kernelspec},
      install_requires=['metakernel', 'mathics'],
      package_data={
          'wolfram_kernel': ['init.m'],
        'wolfram_kernel.web': [ 
            'media/css/*.css', 'media/img/*.gif',
            'media/js/innerdom/*.js', 'media/js/prototype/*.js',
            'media/js/scriptaculous/*.js', 'media/js/three/Three.js',
            'media/js/three/Detector.js', 'media/js/*.js', 'templates/*.html',
            'templates/doc/*.html'] + list(subdirs('media/js/mathjax/')),   
      },
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)
