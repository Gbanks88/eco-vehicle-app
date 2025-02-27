from setuptools import setup, find_packages

setup(
    name="eco-vehicle-modeling",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "networkx>=3.0.0",
        "graphviz>=0.20.1",
        "plantuml-markdown>=3.9.0",
        "pydot>=1.4.2",
        "pygraphviz>=1.10",
        "pyyaml>=6.0.1",
        "jsonschema>=4.17.3",
        "matplotlib>=3.7.0",
    ],
    python_requires=">=3.8",
)
