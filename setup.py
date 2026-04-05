from setuptools import setup, find_packages

setup(
    name="flask-helloworld",
    version="1.0.0",
    description="A simple Flask Hello World application",
    author="Wells Teams",
    py_modules=["app"],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "flask>=3.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flask-helloworld=app:app",
        ],
    },
)
