import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysss2",
    version="0.1.dev4",
    author="Simppa Äkäslompolo",
    author_email="simppa.akaslompolo@alumni.aalto.fi",
    description="Tools to interact with the Serpent2 Monte Carlo code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sjjamsa/pysss2",
    packages=setuptools.find_packages(),
    scripts=['bin/pysss2'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha"
    ],
    python_requires='>=3.7',
    install_requires=['psutil','matplotlib>=3.1.1']
)
