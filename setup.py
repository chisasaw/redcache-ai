from setuptools import setup, find_packages  

setup(
    name="redcache-ai", 
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
       "openai", "scikit-learn ", "numpy" 
    ],
    author="Warren Chisasa",
    author_email="warrenchisasa@gmail.com",
    description="A memory framework for Large Language Models and Agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chisasaw/redcache-ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 

