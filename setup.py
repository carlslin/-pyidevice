from setuptools import setup, find_packages
import os
import sys

# 获取README.md内容作为long_description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# 获取版本号
def get_version():
    """从__init__.py获取版本号"""
    version_file = os.path.join(here, 'pyidevice', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

# 检查Python版本
if sys.version_info < (3, 6):
    sys.exit('pyidevice requires Python 3.6 or higher')

setup(
    name='pyidevice',
    version=get_version(),
    description='A comprehensive iOS device automation library based on libimobiledevice',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='pyidevice contributors',
    author_email='pyidevice@example.com',
    url='https://github.com/yourusername/pyidevice',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/pyidevice/issues',
        'Source': 'https://github.com/yourusername/pyidevice',
        'Documentation': 'https://pyidevice.readthedocs.io/',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    include_package_data=True,
    package_data={
        'pyidevice': ['*.json', '*.yaml', '*.yml'],
    },
    install_requires=[
        'fb-idb>=2.0.0',        # 用于UI自动化
        'requests>=2.20.0',     # HTTP请求库
        'psutil>=5.0.0',        # 系统进程管理
    ],
    extras_require={
        'dev': [
            'black>=21.0.0',
            'flake8>=3.8.0',
            'mypy>=0.800',
            'sphinx>=3.0.0',
            'sphinx-rtd-theme>=0.5.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'pyidevice=pyidevice.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
    ],
    keywords='ios automation libimobiledevice idb',
    python_requires='>=3.6',
    zip_safe=False,
)