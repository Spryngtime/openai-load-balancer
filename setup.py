from setuptools import setup, find_packages

setup(
    name='OpenAI Load Balancer',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='The OpenAI Load Balancer is a Python library designed to distribute API requests across multiple endpoints (supports both OpenAI and Azure OpenAI). It implements a round-robin mechanism for load balancing and includes exponential backoff for retrying failed requests.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Rick Liu',
    author_email='rick@spryngtime.com',
    url='https://github.com/Spryngtime/openai-load-balancer',
    install_requires=[
        # Any required packages here
        'openai',
        'python-dotenv',
        'tenacity'
    ],
    classifiers=[
        # Full list at https://pypi.org/classifiers/
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        # Add additional supported Python versions
    ],
)
