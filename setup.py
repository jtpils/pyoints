import setuptools

# get long description from README
with open("README.md", "r") as fh:
    long_description = fh.read()
    
# get requirements
with open('requirements.txt') as f:
    install_requires = []
    for line in f:
        pkgname = line.partition('#')[0].rstrip()
        if pkgname is not '':
            install_requires.append(pkgname)

setuptools.setup (
    name="pointspy",
    version="0.1",
    author="Sebastian Lamprecht",
    author_email="lamprecht@uni-trier.de",    
    description="A python library to conveniently process point cloud data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="TODO",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),

)