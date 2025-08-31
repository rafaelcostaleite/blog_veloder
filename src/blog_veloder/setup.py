from setuptools import setup, find_packages

setup(
    name="triathlon-crew-ai",
    version="1.0.0",
    description="Projeto CrewAI para automação de blog sobre triathlon",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    packages=find_packages(),
    install_requires=[
        "crewai>=0.80.0,<1.0.0",
        "crewai-tools>=0.12.0,<1.0.0",
        "langchain>=0.2.16,<0.3.0",
        "langchain-google-genai>=2.0.0,<3.0.0",
        "langchain-community>=0.2.0,<0.3.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "google-generativeai>=0.8.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

