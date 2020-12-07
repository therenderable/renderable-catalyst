from pathlib import Path
from configparser import ConfigParser

from renderable_core.models import NodeType
from renderable_core.services import APIClient, Machine


class Start:
  def build_parser(self, subparsers):
    parser = subparsers.add_parser('start', description = 'Renderable command to start rendering tasks.',
      help = 'start rendering tasks')

    parser.add_argument('-c', '--cpus',
      help = 'machine cpu count, default is 4', type = int, default = 4)

    parser.add_argument('-m', '--memory',
      help = 'machine memory size (MB), default is 4096', type = int, default = 4096)

    parser.add_argument('-s', '--storage',
      help = 'machine disk size (MB), default is 10240', type = int, default = 10240)

    parser.add_argument('-f', '--force', help = 'force to update the machine', action = 'store_true')

    return parser

  def execute(self, args, logger, configuration_filename):
    cpus = args.cpus
    memory = args.memory
    storage = args.storage
    force = args.force

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
    machine = Machine(machine_name, root_path)

    try:
      if machine.running():
        logger.error('machine already started.')
        exit(1)

      logger.info('starting...')

      if 'device_id' in default_configuration.keys():
        device_id = default_configuration.get('device_id')
        device = client.get_device(device_id)
      else:
        logger.info('registering machine...')
        device = client.register_device(NodeType.worker)

        parser['DEFAULT']['device_id'] = str(device.id)

        with open(configuration_filename, 'w') as file:
          parser.write(file)

      if machine.exists():
        logger.info('updating machine specification...')
        machine.update(cpus, memory, storage, force)
      else:
        logger.info('preparing machine environment...')
        machine.create(cpus, memory, storage)

      machine.join_cluster(device.cluster_address, device.token)
    except:
      logger.error('failed to start machine.')
      exit(1)

    logger.info('success.')
