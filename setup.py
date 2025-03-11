from setuptools import setup, find_packages

setup(
    name='pp2_converter',  # Replace with your package's name
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'tkcalendar',
        'Pillow',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            'currency_converter=pp2_converter.main:main',  # Adjust to match your main function
        ],
    },
    author='Jeffrey R. Dotson',
    author_email='jeffreyrdotson@gmail.com',
    description='Currency exchange rate calculator with a Tkinter GUI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Jeffrey214/VUT-PP2-CurrencyConverter',  # Your GitHub repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
