import DobotDllType as dType
import sys
import os


def communication():
    try:
        arg_input = sys.argv[1]
        if arg_input.lower() in ["-f", "-file"]:
            file_patch = sys.argv[2]
            if not os.path.exists(file_patch):
                print("File path invalid")
                sys.exit(1)
            return arg_input, file_patch
        elif arg_input.lower() in ["-c", "-cmd"]:
            return arg_input, 0
        elif arg_input.lower() in ["h", "help"]:
            return arg_input, 0
        else:
            print("incorrect syntax")
            sys.exit(1)
    except IndexError:
        print("incorrect syntax")
        sys.exit(1)


CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


def help_command():
    print('|  Help => help command with list of commands and arguments.\n'
          '|  example: "python DobotControl.py help"\n|\n'
          '|  Argument 1 = c/cmd or f/file => determines way of communication.\n'
          '|  usage: -c/-cmd => commands provided via cmd.\n'
          '|         -f/-file => commands provided via file.\n'
          '|  example:"Python DobotControl.py -cmd".\n|\n'
          '|  Argument 2 => file path if -f/-file argument used.\n'
          '|  example:"python DobotControl.py -f ./docs/files/file.txt".\n'
          '|\n'
          '|  Commands -> commands are used to control dobot arm\n'
          '|  G01 => move to xyzr coordinate.\n'
          '|  syntax: G01 Xx Yy Zz Rr\n'
          '|  example: G01 X100 Y100 Z100 R0 => move to point (100, 100, 100) and rotare tool 0 degrees\n'
          '|  G04 => wait p milliseconds.\n'
          '|  syntax: G04 Pp\n'
          '|  example: G04 P1000 => wait 1s\n'
          '|  G28 => move to home coordinates\n'
          '|  M02 => end of program\n'
          '|  M03 => tool on.\n'
          '|  M04 => change tool state to close (gripper only).\n'
          '|  M05 => tool off.\n'
          '|  M06 => tool change.\n'
          '|  syntax: M06 Tt\n'
          '|  arguments:\n'
          '|            T1 => pen\n'
          '|            T2 => suction\n'
          '|            T3 => gripper\n'
          '|            T4 => laser\n'
          '|            T5 => printer\n'
          '|  V1.0 Thanks for use. Program author Jakub Malinowski')


def com(arg, lines, api, tool, last_index):
    val1 = None
    val2 = None
    val3 = None
    val4 = None
    # val5 = None
    valu1 = None
    valu2 = None
    valu3 = None
    valu4 = None
    val = lines.strip().split(" ")
    if val[0] == "G01":
        if len(val) >= 1:
            val1 = val[1]
        if len(val) >= 2:
            val2 = val[2]
        if len(val) >= 3:
            val3 = val[3]
        if len(val) >= 4:
            val4 = val[4]
        if val1 and val1[:1] == "X":
            valu1 = int(val1[1:])
        if val2 and val2[:1] == "Y":
            valu2 = int(val2[1:])
        if val3 and val3[:1] == "Z":
            valu3 = int(val3[1:])
        if val4 and val4[:1] == "R":
            valu4 = int(val4[1:])
        last_index = \
            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, valu1, valu2, valu3, valu4, isQueued=1)[
                0]
    if val[0] == "G04" and len(val) >= 1:
        val1 = val[1]
        if val1 and val1[:1] == "P":
            valu1 = int(val1[1:])
            last_index = dType.SetWAITCmd(api, waitTime=valu1, isQueued=1)[0]
    if val[0] == 'M02' and len(val) == 1:
        print('Finished')
        if arg == 'cmd':
            return 0, 0
    if val[0] == 'G28' and len(val) == 1:
        print('homing')
        dType.SetHOMECmd(api, temp=0, isQueued=1)
    if val[0] == "M06" and len(val) >= 1:
        val1 = val[1]
        if val1 and val1[:1] == "T":
            valu1 = int(val1[1:])
            if valu1 and valu1 in [1, 2, 3, 4, 5]:
                tool = valu1
                return 2, tool
    if val[0] == "M03" and len(val) == 1 and tool != 0:
        if tool == 1:
            print('')  # pen
        if tool == 2:
            last_index = dType.SetEndEffectorSuctionCup(api, enableCtrl=1, on=1, isQueued=1)[0]
        if tool == 3:
            last_index = dType.SetEndEffectorGripper(api, enableCtrl=1, on=1, isQueued=1)[0]
        if tool == 4:
            last_index = dType.SetEndEffectorLaser(api, enableCtrl=1, on=1, isQueued=1)[0]
        if tool == 5:
            print('')  # printer
    if val[0] == "M04" and tool != 0:
        if tool == 3:
            last_index = dType.SetEndEffectorGripper(api, enableCtrl=1, on=0, isQueued=1)[0]
    if val[0] == "M05" and len(val) == 1 and tool != 0:
        if tool == 1:
            print('')  # pen
        if tool == 2:
            last_index = dType.SetEndEffectorSuctionCup(api, enableCtrl=0, on=0, isQueued=1)[0]
        if tool == 3:
            last_index = dType.SetEndEffectorGripper(api, enableCtrl=0, on=0, isQueued=1)[0]
        if tool == 4:
            last_index = dType.SetEndEffectorLaser(api, enableCtrl=0, on=0, isQueued=1)[0]
        if tool == 5:
            print('')  # printer
    return 1, last_index


def com_cmd():
    tool = 0
    api = dType.load()
    state = dType.ConnectDobot(api, "", 115200)[0]
    print("Connect status:", CON_STR[state])
    if state == dType.DobotConnect.DobotConnect_NoError:

        dType.SetQueuedCmdClear(api)
        dType.SetHOMEParams(api, 200, 0, 0, 0, isQueued=1)
        dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
        dType.SetPTPCommonParams(api, 100, 100, isQueued=1)
        dType.SetHOMECmd(api, temp=0, isQueued=1)
        last_index = dType.SetHOMECmd(api, temp=0, isQueued=1)

        print('CMD INPUT')
        while True:
            try:
                lines = str(input(''))
                result = com('cmd', lines, api, tool, last_index)
                if result[0] == 0 and result[1] == 0:
                    break
                elif result[0] == 1:
                    last_index = result[1]
                elif result[0] == 2:
                    tool = result[1]
            except Exception as e:
                print("Error occurred while command execution:", e)

            dType.SetQueuedCmdStartExec(api)
            try:
                if isinstance(last_index, list):
                    last_index = last_index[0]
                while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
                    dType.dSleep(100)
            except TypeError:
                print('something went wromg')
                continue
            dType.SetQueuedCmdStopExec(api)

    dType.DisconnectDobot(api)


def com_file(file_patch):
    tool = 0
    api = dType.load()
    state = dType.ConnectDobot(api, "", 115200)[0]
    print("Connect status:", CON_STR[state])

    if state == dType.DobotConnect.DobotConnect_NoError:

        dType.SetQueuedCmdClear(api)
        dType.SetHOMEParams(api, 200, 0, 0, 0, isQueued=1)
        dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
        dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

        dType.SetHOMECmd(api, temp=0, isQueued=1)
        last_index = dType.SetHOMECmd(api, temp=0, isQueued=1)

        # to wymaga poprawienia \|/
        print('FILE INPUT')
        try:
            with open(file_patch, 'r') as plik:
                lines = plik.readlines()
                for line in lines:
                    result = com('file', line, api, tool, last_index)
                    if result[0] == 0 and result[1] == 0:
                        break
                    elif result[0] == 1:
                        last_index = result[1]
                    elif result[0] == 2:
                        tool = result[1]

        except Exception as e:
            print("Error occurred while file read:", e)

        dType.SetQueuedCmdStartExec(api)
        if isinstance(last_index, list):
            last_index = last_index[0]
        while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)
        print('Finished')
        dType.SetQueuedCmdStopExec(api)

    dType.DisconnectDobot(api)


def main():
    come = communication()
    if come[0].lower() in ["-c", "-cmd"]:
        com_cmd()
    elif come[0].lower() in ['-f', '-file']:
        com_file(come[1])
    elif come[0].lower() in ["h", "help"]:
        help_command()


if __name__ == '__main__':
    main()
