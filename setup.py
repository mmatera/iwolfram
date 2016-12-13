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



# As default, look first if wolfram mma is installed. Otherwise, use mathics. 
wmmexec = None
if "--mma-exec" in sys.argv:
    idx = sys.argv.index("--mma-exec")
    sys.argv.pop(idx)
    candidate = sys.argv.pop(idx)
    try:
        starttext = os.popen("bash -c 'echo |" +  candidate  +"'").read()
        if starttext[:11] == "Mathematica":			      
            print("Using Wolfram Mathematica")
            wmmexec = candidate
        elif starttext[:8] == "\nMathics":			      
            print("Using Mathics")
            wmmexec = candidate
    except Exception:
        print(wmmexec  + " is not a valid interpreter. Looking for a valid one.")
            
if wmmexec is None:
    candidates =  [os.path.join(path, 'MathKernel') for path in os.environ["PATH"].split(os.pathsep) 
                   if os.access(os.path.join(path, 'MathKernel'), os.X_OK)]
    for candidate in candidates:    
        try:
            starttext = os.popen("bash -c 'echo |" +  candidate  +"'").read()
            if starttext[:11] == "Mathematica":			      
                print("MathKernel (Wolfram version) found at " + candidate)
                wmmexec = candidate
                break
        except Exception:
            continue

if wmmexec is None:
    candidates =  [os.path.join(path, 'mathics') for path in os.environ["PATH"].split(os.pathsep) 
                   if os.access(os.path.join(path, 'mathics'), os.X_OK)]
    for candidate in candidates:    
        try:
            starttext = os.popen("bash -c 'echo |" +  candidate  +"'").read()
            if starttext[:8] == "\nmathics":			      
                print("Mathics version found at " + candidate)
                wmmexec = candidate
                break
        except Exception:
            continue

if wmmexec is None:
    print("couldn't find a mathics/mathematica interpreter.")
    sys.exit(-1)

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
        global wmmexec
        configfilestr = "# iwolfram configuration file\nmathexec = '{wolfram-caller-script-path}'\n\n"
        configfilestr = configfilestr.replace('{wolfram-caller-script-path}',wmmexec)
        with open('wolfram_kernel/config.py','w') as f:
            f.write(configfilestr)

        #Run the standard intallation
        install.run(self)

        def install_kernelspec(self):
            from ipykernel.kernelspec import write_kernel_spec
            from jupyter_client.kernelspec import KernelSpecManager
            from wolfram_kernel.wolfram_kernel import WolframKernel
            kernel_json = WolframKernel.kernel_json
        
            kernel_spec_manager = KernelSpecManager()
            log.info('Writing kernel spec')
            kernel_spec_path = write_kernel_spec(overrides=kernel_json)
            log.info('Installing kernel spec')
            try:
                kernel_spec_manager.install_kernel_spec(
                    kernel_spec_path,
                    kernel_name=kernel_json['name'],
                        user=self.user)
            except:
                log.error('Failed to install kernel spec in ' + kernel_spec_path)
                
        print("Installing kernel spec")        
        #Build and Install the kernelspec
        install_kernelspec(self)
        log.info("Installing nbextension")
        from notebook.nbextensions import install_nbextension        
        try:
            install_nbextension(os.path.join(os.path.dirname(__file__), 'nbmathics'),overwrite=True,)
        except:
            log.info("nbextension can not be installed")
        
        

setup(name='wolfram_kernel',
      version='0.11.3',
      description='A Wolfram Mathematica/mathics kernel for Jupyter/IPython',
      long_description='A Wolfram Mathematica/mathics kernel for Jupyter/IPython, based on MetaKernel',
      url='https://github.com/matera/iwolfram/tree/master/iwolfram',
      author='Juan Mauricio Matera',
      author_email='matera@fisica.unlp.edu.ar',
      packages=['wolfram_kernel','nbmathics'],
      cmdclass={'install': install_with_kernelspec},
      install_requires=['metakernel', 'mathics'],
      package_data={
          'wolfram_kernel': ['init.m'],
          'nbmathics': ['nbmathics/static/img/*.gif',
                        'nbmathics/static/css/*.css',
                        'nbmathics/static/*.js',
                        'nbmathics/static/js/*.js',
                        'nbmathics/static/js/innerdom/*.js',
                        'nbmathics/static/js/prototype/*.js',
                        'nbmathics/static/js/scriptaculous/*.js',
                        'nbmathics/static/js/tree/Three.js',
                        'nbmathics/static/js/tree/Detector.js',
                         ] + list(subdirs('media/js/mathjax/')),   
      },
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)
