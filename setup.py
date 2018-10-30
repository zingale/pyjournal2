from setuptools import setup, find_packages

setup(name='pyjournal2',
      version='1.0.0',
      description='a simple sphinx- & git-based research journal',
      url='https://github.com/zingale/pyjournal2',
      author='Mike Zingale',
      author_email='michael.zingale@stonybrook.edu',
      license='BSD',
      packages=find_packages(),
      scripts=["pyjournal.py"],
      package_data={"pyjournal2": ["sphinx_base/*", "sphinx_base/source/*", "sphinx_base/source/main/*", "sphinx_base/source/_static/*", "sphinx_base/source/_templates/*"]},
      zip_safe=False)
