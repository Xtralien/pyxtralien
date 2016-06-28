from xtralien.imports import *

def prompt(vars=None, message="" ):
    #prompt_message = "Welcome!  Useful: G is the graph, DB, C"
    prompt_message = message
    try:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed(argv=[''],banner=prompt_message,exit_msg="Exiting...")
        return  ipshell()
    except ImportError:
        if vars is None:  vars=globals()
        import code
        import rlcompleter
        import readline
        readline.parse_and_bind("tab: complete")
        # calling this with globals ensures we can see the environment
        print(prompt_message)
        shell = code.InteractiveConsole(vars)
        return shell.interact()

prompt_ = prompt()
