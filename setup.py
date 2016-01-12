from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='agu_data',
      version='1.0',
      description='Package from scratching AGU website',
      classifiers=[
          'Development Status :: 1 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: AGU',
      ],
      keywords='AGU, Abstracts, Papers',
      url='https://github.com/cthorey/agu_data',
      author='Thorey Clement',
      author_email='clement.thorey@gmail.com',
      license='MIT',
      packages=['agu_data'],
      install_requires=[
          'selenium',
          'tqdm',
          'BeautifulSoup'],
      include_package_data=True,
      zip_safe=False)
