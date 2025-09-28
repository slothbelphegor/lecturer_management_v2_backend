from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lecturers-management-backend",
    version="0.1.0",
    author="slothbelphegor",
    author_email="andinhtran123@gmail.com",
    description="A Django backend for lecturer management system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slothbelphegor/lecturer_management_v2_frontend",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        '': ['templates/*.*'],
    },
)