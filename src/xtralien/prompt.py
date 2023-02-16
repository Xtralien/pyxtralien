from xtralien.imports import *  # noqa: F403


def prompt(vars=None, message=""):
    prompt_message = message
    try:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed(
            argv=[''],
            banner=prompt_message,
            exit_msg="Exiting..."
        )
        return ipshell()
    except ImportError:
        if vars is None:
            vars = globals()
        import code
        import rlcompleter  # noqa: F401
        import readline
        readline.parse_and_bind("tab: complete")
        print(prompt_message)
        shell = code.InteractiveConsole(vars)
        return shell.interact()

prompt_ = prompt()
