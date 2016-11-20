import nbformat
import os
import io

def _jupyter_server_extension_path():
    return [{'module':"nbmathics"}]

def _juputer_nbextension_paths():
    return [dict(
        section = "notebook",
        src = "static",
        dest = "nbmathics",
        require = "nbmathics/main"
    )]

def _juputer_bundlerextension_paths():
    return [{
    

    }]


def bundler(handler, model):
    notebook_filename = model['name']
    notebook_content = nbformat.writes(model['content']).encode('utf-8')
    notebook_name = os.path.splitext(notebook_filename)[0]
    m_filename = '{}.m'.format(notebook_name)
    handler.set_header('Content-Disposition',
                       'attachment; filename="{}"'.format(m_filename))
    handler.set_header('Content-Type','application/mathematica.package')
    handler.finish(notebook_content)



def load_jupyter_server_extension(nbapp):
    nbapp.log.info("nbmathics enabled!")

