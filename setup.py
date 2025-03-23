from setuptools import setup, find_packages

setup(
    name="secure-config-loader",
    use_scm_version=True, # 添加动态版本管理
    setup_requires=["setuptools_scm"], # 添加依赖
    author="aiziyuer",
    author_email="910217951@qq.com",
    description="Secure multi-format configuration loader with Ansible Vault support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aiziyuer/secure-config-loader",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "ansible-core>=2.13",
        "python-box>=6.0",
        "PyYAML>=6.0",
        "toml>=0.10",
        "python-dotenv>=0.19",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
