import logging

from . import commands, CLI


def main():
  logging.basicConfig()

  logger = logging.getLogger('renderable-catalyst')
  logger.setLevel(logging.INFO)

  subcommands = [
    commands.Start(),
    commands.Stop(),
    commands.Render(),
    commands.Status()
  ]

  cli = CLI(subcommands)
  cli.run(logger)


if __name__ == '__main__':
  main()
