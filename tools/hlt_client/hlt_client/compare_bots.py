import json
import subprocess

from . import output

_SPACE_DELIMITER = ' '
_BOT_ID_POSITION = 1


def _determine_winner(game_result):
    """
    From the game result string, extract the winner's id.
    :param game_result: The result of running a game on the Halite binary
    :return:
    """
    results = json.loads(game_result)
    for player_id, stats in results["stats"].items():
        if stats["rank"] == 1:
            return player_id


def _play_game(binary, map_width, map_height, bot_commands, flags):
    """
    Plays one game considering the specified bots and the game and map constraints.
    :param binary: The halite binary
    :param map_width: The map width
    :param map_height: The map height
    :param bot_commands: The commands to run each of the bots
    :return: The game's result string
    """
    command = [
        binary,
        "--width", str(map_width),
        "--height", str(map_height),
        "--results-as-json"
    ]
    command.extend(flags)
    for bot_command in bot_commands:
        command.append(bot_command)
    return subprocess.check_output(command).decode()


def play_games(binary, map_width, map_height, bot_commands, number_of_runs, flags):
    """
    Runs number_of_runs games using the designated bots and binary, recording the tally of wins per player
    :param binary: The Halite binary.
    :param map_width: The map width
    :param map_height: The map height
    :param bot_commands: The commands to run each of the bots (must be either 2 or 4)
    :param number_of_runs: How many runs total
    :return: Nothing
    """
    # TODO: way to choose where log files, etc. go (chdir)
    output.output("Comparing Bots!")
    result = {}
    if not(len(bot_commands) == 4 or len(bot_commands) == 2):
        raise IndexError("The number of bots specified must be either 2 or 4.")
    for current_run in range(0, number_of_runs):
        match_output = _play_game(binary, map_width, map_height, bot_commands, flags)
        winner = _determine_winner(match_output)
        result[winner] = result.setdefault(winner, 0) + 1
        output.output("Finished {} runs.".format(current_run + 1), games_played=current_run + 1)
        output.output("Win Ratio: {}".format(result), stats=result)


def parse_arguments(subparser):
    bot_parser = subparser.add_parser('gym', help='Train your Bot(s)!')
    bot_parser.add_argument('-r', '--run-command',
                            dest='run_commands',
                            action='append',
                            type=str, required=True,
                            help="The command to run a specific bot. You may pass either 2 or 4 of these arguments")
    bot_parser.add_argument('-b', '--binary',
                            dest='halite_binary',
                            action='store',
                            type=str, required=True,
                            help="The halite executable/binary path, used to run the games")

    bot_parser.add_argument('-W', '--width',
                            dest='map_width',
                            action='store',
                            type=int, default=48,
                            help="The map width the simulations will run in")
    bot_parser.add_argument('-H', '--height',
                            dest='map_height',
                            action='store',
                            type=int, default=48,
                            help="The map height the simulations will run in")
    bot_parser.add_argument('-i', '--iterations',
                            dest='iterations',
                            action='store',
                            type=int,  default=100,
                            help="Number of games to be run")
