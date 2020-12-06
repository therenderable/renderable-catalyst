import argparse
from pathlib import Path

from .. import package


class CLI:
  def __init__(self, commands):
    self.commands = commands
    self.command_map = {type(command).__name__.lower(): command for command in self.commands}

  def build_parser(self):
    parser = argparse.ArgumentParser(description = 'Renderable desktop client.')

    application_name = package.__title__.lower().replace(' ', '-')
    configuration_filename = str((Path.home() / Path(f'.{application_name}/configuration.ini')).resolve())

    parser.add_argument('-c', '--configuration',
      help = f'configuration file, default is "{configuration_filename}"',
      type = str,
      default = configuration_filename)

    parser.add_argument('-v', '--version',
      help = 'show version', action = 'version', version = package.__version__)

    subparsers = parser.add_subparsers(dest = 'command', metavar = '<command>')

    for command in self.commands:
      command.build_parser(subparsers)

    return parser

  def run(self, logger):
    parser = self.build_parser()
    args = parser.parse_args()

    configuration_filename = Path(args.configuration)
    command = args.command

    if not configuration_filename.is_file():
      logger.error('cannot found configuration file.')
      exit(1)

    if command is None:
      parser.print_usage()
    else:
      self.command_map[command].execute(args, logger, configuration_filename)
