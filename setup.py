from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="conf_root",  # 包名
    version="0.4.1",  # 版本号
    install_requires=[
        "ruamel.yaml>=0.18.6",
        "wtforms>=3.1.2",
        "jinja2>=3.1.4"
    ],
    author="ciaranchen",
    author_email="ciaranchen@qq.com",
    description="基于dataclass的配置文件取用工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ciaranchen/conf_root",
    packages=["conf_root", "conf_root.agents"],  # 包含的Python模块或子包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',  # 兼容的Python版本
    entry_points={
        "console_scripts": [
            'conf-root-web: conf_root.ConfRoot:main'
        ],
    },
)
