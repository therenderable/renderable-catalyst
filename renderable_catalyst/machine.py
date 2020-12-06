#
import platform
import subprocess


class Machine:
  def __init__(self, name, path):
    self.name = name
    self.path = path

    executable_intermediate_path = self.path / 'bin'

    self.executable = executable_intermediate_path / 'docker-machine'

  def command_from_args(self, args):
    return f'{self.executable} --storage-path {self.path} {args}'

  def exists(self):
    command = self.command_from_args('ls')

    output = subprocess.check_output(command, shell = True).decode().strip().split('\n')
    name_index = output[0].split().index('NAME')

    machines = output[1:]
    machine_names = [machine.split()[name_index] for machine in machines]

    return self.name in machine_names

  def create(self):
    if platform.system() == 'Windows':
      command = self.command_from_args(f'create --driver hyperv --hyperv-virtual-switch "Default Switch" {self.name}')
    else:
      command = self.command_from_args(f'create --driver virtualbox {self.name}')

    subprocess.check_call(command, shell = True)

  def start(self, cluster_address, token):
    command = self.command_from_args(f'start {self.name}')

    subprocess.check_call(command, shell = True)

  def stop(self):
    command = self.command_from_args(f'stop {self.name}')

    subprocess.check_call(command, shell = True)
