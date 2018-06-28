import app_settings

def write_file(output_data):
    file = open(app_settings.OUTPUT_PATH + app_settings.OUTPUT_FILE, "w");
    file.write(get_team_info('main', app_settings.TEAM_NAME, app_settings.EMAIL))
    rows = len(output_data)
    columns = len(output_data[0])

    if(columns != app_settings.NR_OF_TRACKS+1):
        print("Not enough columns!")
        SystemExit(0)

    for i in range(rows):
        joinData = ', '.join(map(str, output_data[i]));
        file.write(joinData + '\n')
            
    file.close();

def get_team_info(challenge_track, team_name, email):
    teamFormat = "team_info,{0},{1},{2} \n"
    return teamFormat.format(challenge_track, team_name, email)