from setuptools import setup, find_packages

setup(
    name='langchain-demo',
    version='1.0.0',
    description='A Python Langchain Project Demo',
    author='Raghavendra Puttappa',
    author_email='puttappa.raghavendra@gmail.com',
    packages=find_packages(),
    install_requires=[
        # Add your project dependencies here
    ],
    entry_points={
        'console_scripts': [
            'langchain-demo = src.main:main'
        ]
    },
)