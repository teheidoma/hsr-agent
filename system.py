import subprocess
def is_game_running():
    run = subprocess.run('tasklist', capture_output='stdout')
    tasks = run.stdout
    return str(tasks).find("StarRail.exe") != -1