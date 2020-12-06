from pathlib import Path
from configparser import ConfigParser

#
from ... import machine as m


class Stop:
  def build_parser(self, subparsers):
    parser = subparsers.add_parser('stop', description = 'Renderable command to stop rendering tasks.',
      help = 'stop rendering tasks')

    return parser

  def execute(self, args, logger, configuration_filename):
    try:
      parser = ConfigParser()
      parser.read(configuration_filename)

      default_configuration = parser['DEFAULT']

      root_path = Path(default_configuration.get('root_path'))
      machine_name = default_configuration.get('machine_name')
    except:
      logger.error('invalid configuration file.')
      exit(1)

    machine = m.Machine(machine_name, root_path)

    if not machine.exists():
      logger.error('machine already stopped.')
      exit(1)

    logger.info('stopping...')

    try:
      machine.stop()
    except:
      logger.error('failed to stop machine.')
      exit(1)

    logger.info('success.')
