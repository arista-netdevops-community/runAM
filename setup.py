import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="runAM-evpn",
    version="0.1.1",
    description="runAM Python modules to build EVPN network",
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/arista-netdevops-community/runAM',
    author='Petr Ankudinov',
    license="BSD",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "argcomplete==1.12.1",
        "glom==20.11.0",
        "jq==1.1.1",
        "PyYAML==5.3.1",
    ],
    entry_points = {
        "console_scripts": ['runAM = runAM.cli:interpreter']
    },
)
