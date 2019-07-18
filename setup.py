#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="RYTD",
    version="0.1",
    packages=find_packages(),
    install_requires=["pytube", "mutagen", "youtube_dl"],
    author="Me",
    author_email="me@example.com",
    description="Ein Youtube downloader von der feinsten Sorte.",
    keywords="youtube downloader",
    url="https://gitea.gelse.eu/Riedler/RYTD",
    classifiers=[])