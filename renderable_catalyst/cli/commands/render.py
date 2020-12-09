from pathlib import Path
from configparser import ConfigParser

from renderable_core import utils
from renderable_core.models import FrameRange, JobRequest
from renderable_core.services import APIClient


class Render:
  def build_parser(self, subparsers):
    parser = subparsers.add_parser('render', description = 'Renderable command to dispatch scenes to rendering queue.',
      help = 'dispatch scene to rendering queue')

    parser.add_argument('-s', '--scene_path', help = 'scene path', type = str, required = True)

    parser.add_argument('-fs', '--frame_start', help = 'frame start', type = int, required = True)

    parser.add_argument('-fe', '--frame_end', help = 'frame end', type = int, required = True)

    parser.add_argument('-c', '--container_name', help = 'container name', type = str, required = True)

    parser.add_argument('-p', '--parallelism',
      help = 'parallelism parameter, default is 4', type = int, default = 4)

    return parser

  def execute(self, args, logger, configuration_filename):
    scene_path = Path(args.scene_path)
    frame_start = args.frame_start
    frame_end = args.frame_end
    container_name = args.container_name
    parallelism = args.parallelism

    if not scene_path.is_file():
      logger.error('invalid scene path.')
      exit(1)

    job = JobRequest(
      parallelism = parallelism,
      container_name = container_name,
      frame_range = FrameRange(start = frame_start, end = frame_end))

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
      logger.info('enqueueing...')
      job_response = client.submit_job(job, scene_path)
    except:
      logger.error('failed to enqueue scene.')
      exit(1)

    try:
      print(utils.job_statistics([job_response]), end = '\r')

      def callback(response):
        print(utils.job_statistics([response]), end = '\r')

      client.listen_job(job_response.id, callback)
    except:
      logger.error('failed to retrieve job status.')
      exit(1)
