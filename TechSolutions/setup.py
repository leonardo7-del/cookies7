from setuptools import setup, find_packages

setup(
    name="tech_solutions",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python>=8.0.0",
        "reportlab>=3.6.0",
        "python-dotenv>=0.19.0"
    ],
    entry_points={
        'console_scripts': [
            'techsolutions=main:main',
        ],
    },
)