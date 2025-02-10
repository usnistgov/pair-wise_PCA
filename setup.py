from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
version = open("pcatool/version.py").readlines()[-1].split()[-1].strip("\"'")

setup(
    name='pairwise_pcatool',
    version=version,
    description='PCA Inspection Tool For Nist Diverse Communities Data Excerpts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='National Institute of Standards and Technology',
    packages=["pcatool",
              "pcatool.views",
              "pcatool.views.components",
              "pcatool.views.entry",
              "pcatool.views.main",
              "pcatool.views.main.controls"],
    install_requires=[
        "matplotlib==3.9.2",
        "numpy==1.26.4",
        "pandas==2.2.2",
        "pygame==2.6.0",
        "requests==2.32.3",
        "scikit-learn==1.5.1",
        "tqdm==4.66.0",
    ],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 3.8',
                 'License :: Public Domain',
                 'Intended Audience :: Science/Research'],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pcatool = pcatool.__main__:run",
        ]
    }
)
