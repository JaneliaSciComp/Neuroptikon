from setuptools import setup
setup(name='osgswig',
      version='3.2.1',
      description='Python OpenSceneGraph 3.2.1 Swig Bindings',
      packages=['osgswig'],
      package_dir={'osgswig': '.'},
      package_data={'osgswig': ['*.pyd','_*.so','./examples/*.py']},
      author='http://code.google.com/p/osgswig/people/list',
      url='http://code.google.com/p/osgswig',      
      )
