from configparser import ConfigParser

from renderable_core import utils
from renderable_core.services import APIClient


class Status:
  def build_parser(self, subparsers):
    parser = subparsers.add_parser('status', description = 'Renderable command to inspect job by ID.',
      help = 'inspect job by ID')

    parser.add_argument('-id', '--job_id', help = 'ID to inspect', type = str, required = True)

    return parser

  def execute(self, args, logger, configuration_filename):
    job_id = args.job_id

    try:
      parser = ConfigParser()
      parser.read(configuration_filename)

      default_configuration = parser['DEFAULT']

      api_hostname = default_configuration.get('api_hostname')
      api_port = default_configuration.getint('api_port')
      api_version = default_configuration.get('api_version')
      api_secure = default_configuration.getboolean('api_secure')
    except:
      logger.error('invalid configuration file.')
      exit(1)

    client = APIClient(api_hostname, api_port, api_version, api_secure)

    try:
      job_response = client.get_job(job_id)

      print(utils.job_statistics([job_response]))

      def callback(response):
        print('\n')
        print(utils.job_statistics([response]))

      client.listen_job(job_response.id, callback)
    except:
      logger.error('failed to retrieve job status.')
      exit(1)
