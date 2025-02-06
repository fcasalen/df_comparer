from setuptools import setup, find_packages

setup(
    name="df_comparer",
    version="0.1.3",
    license="GNU General Public License",
    author="fcasalen",
    author_email="fcasalen@gmail.com",
    description="library to get the difference between two dataframes in a new dataframe",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements.txt').readlines(),
    long_description=open("README.md").read(),
    classifiers=[
        "Development Status :: 5 - Prodution/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11"
    ]
)
