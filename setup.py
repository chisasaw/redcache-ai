from setuptools import setup, find_packages
from pathlib import Path

# Read README with explicit UTF-8 encoding
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="redcache-ai", 
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "openai",
        "scikit-learn",  # Removed space after scikit-learn 
        "numpy" 
    ],
    author="Warren Chisasa",
    author_email="warrenchisasa@gmail.com",
    description="A memory framework for Large Language Models and Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chisasaw/redcache-ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)