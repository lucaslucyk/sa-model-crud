from setuptools import setup, find_packages
from pathlib import Path
import subprocess


def get_version_from_git_tag() -> str:
    version = (
        subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .strip()
    )

    if "-" in version:
        # when not on tag, git describe outputs: "1.3.3-22-gdf81228"
        # pip has gotten strict with version numbers
        # so change it to: "1.3.3+22.git.gdf81228"
        # See: https://peps.python.org/pep-0440/#local-version-segments
        v, i, s = version.split("-")
        version = v + "+" + i + ".git." + s

    assert "-" not in version
    assert "." in version

    return version


sa_modelcrud_version: str = get_version_from_git_tag()

# write version on VERSION file
assert Path("sa_modelcrud/version.py").is_file()
with open("sa_modelcrud/VERSION", "w", encoding="utf-8") as fh:
    fh.write("%s\n" % sa_modelcrud_version)


# get description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# get description from README
with open("requirements.txt", "r", encoding="utf-8") as prf:
    install_requires = prf.read().splitlines()


# get description from README
with open("requirements.dev.txt", "r", encoding="utf-8") as drf:
    extra_dev_requires = drf.read().splitlines()


setup(
    name="sa_modelcrud",
    version=sa_modelcrud_version,
    description="Model CRUD manager to handle databases with asynchronous SQLAlchemy sessions",
    packages=find_packages(),
    package_data={"sa_modelcrud": ["VERSION"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=install_requires,
    extra_requires={"dev": extra_dev_requires},
    url="https://github.com/lucaslucyk/sa-model-crud",
    author="Lucas Lucyk",
    author_email="lucaslucyk@gmail.com",
)
