from setuptools import setup

setup(
    name='zooboss',
    version='0.1.0',
    packages=['zooboss'],
    url='https://github.com/neriberto/zooboss',
    license='BSD 3-Clause License',
    author='Neriberto C.Prado',
    author_email='neriberto@gmail.com',
    description='A malware zoo files organizer',
    entry_points={
        "console_scripts": [
            "zooboss=zooboss:main"
        ],
    }
)
