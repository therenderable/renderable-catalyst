import os
import platform
from pathlib import Path
import urllib
from urllib import request
from configparser import ConfigParser
import subprocess
from distutils.util import convert_path
from distutils.spawn import find_executable
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


def create_application_directory(name):
  directory = Path.home() / f'.{name}'
  os.makedirs(directory, exist_ok = True)

  return directory

def install_virtualbox(version, build_version, directory):
  if find_executable('virtualbox'):
    return

  url = f'https://download.virtualbox.org/virtualbox/{version}/VirtualBox-{version}-{build_version}-Linux_amd64.run'

  intermediate_path = directory / Path('bin')
  path = (intermediate_path / 'virtualbox.run').resolve()

  os.makedirs(intermediate_path, exist_ok = True)

  try:
    request.urlretrieve(url, path)
  except urllib.error.HTTPError as error:
    if error.code == 404:
      raise ValueError('unsupported version')
    else:
      raise error

  subprocess.check_call(f'chmod +x {path} && sh {path} && rm {path}', shell = True)

def install_docker_machine(version, platform_name, directory):
  executable_extension = '.exe' if platform_name == 'Windows' else ''

  url = f'https://github.com/docker/machine/releases/download/v{version}/docker-machine-{platform_name}-x86_64{executable_extension}'

  intermediate_path = directory / Path('bin')
  path = (intermediate_path / f'docker-machine{executable_extension}').resolve()

  os.makedirs(intermediate_path, exist_ok = True)

  try:
    request.urlretrieve(url, path)
  except urllib.error.HTTPError as error:
    if error.code == 404:
      raise ValueError('unsupported platform')
    else:
      raise error

def write_configuration_file(configuration, directory):
  parser = ConfigParser()
  parser['DEFAULT'] = configuration

  path = directory / 'configuration.ini'

  with open(path, 'w') as file:
    parser.write(file)


package_name = 'renderable-catalyst'

virtualbox_version = '6.1.16'
virtualbox_build_version = '140961'
docker_machine_version = '0.16.0'

application_directory = create_application_directory(package_name)

default_configuration = {
  'root_path': str(application_directory.resolve()),
  'api_hostname': 'api.therenderable.com',
  'api_port': 443,
  'api_version': 'v1',
  'api_secure': True,
  'machine_name': 'renderable-machine'
}

package_directory = package_name.replace('-', '_')
package_info = {}

with open(convert_path(f'{package_directory}/package.py'), 'r') as file:
  exec(file.read(), package_info)


def install_dependencies():
  platform_name = platform.system()

  if platform_name != 'Windows':
    install_virtualbox(virtualbox_version, virtualbox_build_version, application_directory)

  #install_docker_machine(docker_machine_version, platform_name, application_directory)
  write_configuration_file(default_configuration, application_directory)


class DevelopCommand(develop):
  def run(self):
    install_dependencies()
    super().run()


class InstallCommand(install):
  def run(self):
    install_dependencies(self)
    super().run()


requirements = [
  'python-docker-machine>=0.2.5',
  'renderable-core@git+https://f2df37d2224599278c1adf7ba248ea3589a85448:x-oauth-basic@github.com/therenderable/renderable-core.git'
]

entrypoints = {
  'console_scripts': [
    f'{package_name} = {package_directory}.cli.__main__:main'
  ]
}

commands = {
  'develop': DevelopCommand,
  'install': InstallCommand
}

setup(
  name = package_name,
  version = package_info['__version__'],
  description = package_info['__description__'],
  author = package_info['__author__'],
  author_email = package_info['__email__'],
  license = package_info['__license__'],
  python_requires = '>=3.7.0',
  install_requires = requirements,
  packages = find_packages(),
  entry_points = entrypoints,
  cmdclass = commands,
  zip_safe = False)
