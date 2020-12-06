from pathlib import Path
from configparser import ConfigParser

from renderable_core.models import NodeType
from renderable_core.services import APIClient

#
from ... import machine as m


class Start:
  def build_parser(self, subparsers):
    parser = subparsers.add_parser('start', description = 'Renderable command to start rendering tasks.',
      help = 'start rendering tasks')

    return parser

  def execute(self, args, logger, configuration_filename):
    try:
      parser = ConfigParser()
      parser.read(configuration_filename)

      default_configuration = parser['DEFAULT']

      root_path = Path(default_configuration.get('root_path'))
      api_hostname = default_configuration.get('api_hostname')
      api_port = default_configuration.getint('api_port')
      api_version = default_configuration.get('api_version')
      api_secure = default_configuration.getboolean('api_secure')
      machine_name = default_configuration.get('machine_name')
    except:
      logger.error('invalid configuration file.')
      exit(1)

    client = APIClient(api_hostname, api_port, api_version, api_secure)
    machine = m.Machine(machine_name, root_path)

    try:
      if 'device_id' in default_configuration.keys():
        device_id = default_configuration.get('device_id')
        device = client.get_device(device_id)
      else:
        device = client.register_device(NodeType.worker)
        parser['DEFAULT']['device_id'] = device.id

        with open(configuration_filename, 'w') as file:
          parser.write(file)
    except:
      logger.error('unable to access API.')
      exit(1)

    if not machine.exists():
      logger.info('preparing environment...')
      machine.create()

    logger.info('starting...')

    try:
      machine.start(machine.cluster_address, machine.token)
    except:
      logger.error('failed to start machine.')
      exit(1)

    logger.info('success.')
