from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="netschoolapi",
    version="3.3.4",
    description="Асинхронный клиент для «Сетевого города»",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kamekuro",
    url="https://github.com/kamekuro/nspy",
    project_urls={
        "Source": "https://github.com/kamekuro/nspy",
        "Issues": "https://github.com/kamekuro/nspy/issues",
    },
    license="GPLv3",
    keywords=[
        "netschool",
        "netschoolapi",
        "netschoolpy",
        "sgo",
        "сетевой город",
        "дневник",
        "госуслуги",
        "esia",
        "education",
        "api",
        "web Education",
        "ir-tech",
        "электронный журнал",
        "school",
        "web2edu",
        "region",
    ],
    packages=["netschoolapi"],
    package_data={"netschoolapi": ["py.typed"]},
    classifiers=[
        "Natural Language :: Russian",
        "Topic :: Education",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "httpx>=0.23",
    ],
    extras_require={
        "qr": ["qrcode>=7.0"],
    },
    python_requires=">=3.10",
)
