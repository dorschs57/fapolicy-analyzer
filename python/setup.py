from setuptools import setup, find_namespace_packages
from setuptools_rust import RustExtension

setup(
    name="fapolicy-analyzer",
    version="0.0.4",
    packages=["fapolicy_analyzer"] + find_namespace_packages(include=['fapolicy_analyzer.*']),
    setup_requires=["setuptools", "setuptools_rust"],
    zip_safe=False,
    rust_extensions=[RustExtension("fapolicy_analyzer.rust"),
                     ],
)