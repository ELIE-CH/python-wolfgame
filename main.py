# -*- coding: utf-8 -*-

import blessed
import random
import time
import socket

term = blessed.Terminal()


# other functions

def create_server_socket(local_port, verbose):
    """Creates a server socket.

    Parameters
    ----------
    local_port: port to listen to (int)
    verbose: True if verbose (bool)

    Returns
    -------
    socket_in: server socket (socket.socket)

    """

    socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_in.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # deal with a socket in TIME_WAIT state

    if verbose:
        print(' binding on local port %d to accept a remote connection' % local_port)

    try:
        socket_in.bind(('', local_port))
    except:
        raise IOError('local port %d already in use by your group or the referee' % local_port)
    socket_in.listen(1)

    if verbose:
        print('   done -> can now accept a remote connection on local port %d\n' % local_port)

    return socket_in


def create_client_socket(remote_IP, remote_port, verbose):
    """Creates a client socket.

    Parameters
    ----------
    remote_IP: IP address to send to (int)
    remote_port: port to send to (int)
    verbose: True if verbose (bool)

    Returns
    -------
    socket_out: client socket (socket.socket)

    """

    socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # deal with a socket in TIME_WAIT state

    connected = False
    msg_shown = False

    while not connected:
        try:
            if verbose and not msg_shown:
                print(' connecting on %s:%d to send orders' % (remote_IP, remote_port))

            socket_out.connect((remote_IP, remote_port))
            connected = True

            if verbose:
                print('   done -> can now send orders to %s:%d\n' % (remote_IP, remote_port))
        except:
            if verbose and not msg_shown:
                print('   connection failed -> will try again every 100 msec...')

            time.sleep(.1)
            msg_shown = True

    return socket_out


def wait_for_connection(socket_in, verbose):
    """Waits for a connection on a server socket.

    Parameters
    ----------
    socket_in: server socket (socket.socket)
    verbose: True if verbose (bool)

    Returns
    -------
    socket_in: accepted connection (socket.socket)

    """

    if verbose:
        print(' waiting for a remote connection to receive orders')

    socket_in, remote_address = socket_in.accept()

    if verbose:
        print('   done -> can now receive remote orders from %s:%d\n' % remote_address)

    return socket_in


def create_connection(your_group, other_group=0, other_IP='127.0.0.1', verbose=False):
    """Creates a connection with a referee or another group.

    Parameters
    ----------
    your_group: id of your group (int)
    other_group: id of the other group, if there is no referee (int, optional)
    other_IP: IP address where the referee or the other group is (str, optional)
    verbose: True only if connection progress must be displayed (bool, optional)

    Returns
    -------
    connection: socket(s) to receive/send orders (dict of socket.socket)

    Raises
    ------
    IOError: if your group fails to create a connection

    Notes
    -----
    Creating a connection can take a few seconds (it must be initialised on both sides).

    If there is a referee, leave other_group=0, otherwise other_IP is the id of the other group.

    If the referee or the other group is on the same computer than you, leave other_IP='127.0.0.1',
    otherwise other_IP is the IP address of the computer where the referee or the other group is.

    The returned connection can be used directly with other functions in this module.

    """

    # init verbose display
    if verbose:
        print('\n[--- starts connection -----------------------------------------------------\n')

    # check whether there is a referee
    if other_group == 0:
        if verbose:
            print('** group %d connecting to referee on %s **\n' % (your_group, other_IP))

        # create one socket (client only)
        socket_out = create_client_socket(other_IP, 42000 + your_group, verbose)

        connection = {'in': socket_out, 'out': socket_out}

        if verbose:
            print('** group %d successfully connected to referee on %s **\n' % (your_group, other_IP))
    else:
        if verbose:
            print('** group %d connecting to group %d on %s **\n' % (your_group, other_group, other_IP))

        # create two sockets (server and client)
        socket_in = create_server_socket(42000 + your_group, verbose)
        socket_out = create_client_socket(other_IP, 42000 + other_group, verbose)

        socket_in = wait_for_connection(socket_in, verbose)

        connection = {'in': socket_in, 'out': socket_out}

        if verbose:
            print('** group %d successfully connected to group %d on %s **\n' % (your_group, other_group, other_IP))

    # end verbose display
    if verbose:
        print('----------------------------------------------------- connection started ---]\n')

    return connection


def bind_referee(group_1, group_2, verbose=False):
    """Put a referee between two groups.

    Parameters
    ----------
    group_1: id of the first group (int)
    group_2: id of the second group (int)
    verbose: True only if connection progress must be displayed (bool, optional)

    Returns
    -------
    connections: sockets to receive/send orders from both players (dict)

    Raises
    ------
    IOError: if the referee fails to create a connection

    Notes
    -----
    Putting the referee in place can take a few seconds (it must be connect to both groups).

    connections contains two connections (dict of socket.socket) which can be used directly
    with other functions in this module.  connection of first (second) player has key 1 (2).

    """

    # init verbose display
    if verbose:
        print('\n[--- starts connection -----------------------------------------------------\n')

    # create a server socket (first group)
    if verbose:
        print('** referee connecting to first group %d **\n' % group_1)

    socket_in_1 = create_server_socket(42000 + group_1, verbose)
    socket_in_1 = wait_for_connection(socket_in_1, verbose)

    if verbose:
        print('** referee succcessfully connected to first group %d **\n' % group_1)

        # create a server socket (second group)
    if verbose:
        print('** referee connecting to second group %d **\n' % group_2)

    socket_in_2 = create_server_socket(42000 + group_2, verbose)
    socket_in_2 = wait_for_connection(socket_in_2, verbose)

    if verbose:
        print('** referee succcessfully connected to second group %d **\n' % group_2)

        # end verbose display
    if verbose:
        print('----------------------------------------------------- connection started ---]\n')

    return {1: {'in': socket_in_1, 'out': socket_in_1},
            2: {'in': socket_in_2, 'out': socket_in_2}}


def close_connection(connection):
    """Closes a connection with a referee or another group.

    Parameters
    ----------
    connection: socket(s) to receive/send orders (dict of socket.socket)

    """

    # get sockets
    socket_in = connection['in']
    socket_out = connection['out']

    # shutdown sockets
    socket_in.shutdown(socket.SHUT_RDWR)
    socket_out.shutdown(socket.SHUT_RDWR)

    # close sockets
    socket_in.close()
    socket_out.close()


def notify_remote_orders(connection, orders):
    """Notifies orders to a remote player.

    Parameters
    ----------
    connection: sockets to receive/send orders (dict of socket.socket)
    orders: orders to notify (str)

    Raises
    ------
    IOError: if remote player cannot be reached

    """

    # deal with null orders (empty string)
    if orders == '':
        orders = 'null'

    # send orders
    try:
        connection['out'].sendall(orders.encode())
    except:
        raise IOError('remote player cannot be reached')


def get_remote_orders(connection):
    """Returns orders from a remote player.

    Parameters
    ----------
    connection: sockets to receive/send orders (dict of socket.socket)

    Returns
    ----------
    player_orders: orders given by remote player (str)

    Raises
    ------
    IOError: if remote player cannot be reached

    """

    # receive orders
    try:
        orders = connection['in'].recv(65536).decode()
    except:
        raise IOError('remote player cannot be reached')

    # deal with null orders
    if orders == 'null':
        orders = ''

    return orders


def extract_ano_file(ano_file):
    """Extract all information from the file.ano
    Parameters :
    -----------
    anoFile : the path of the file.ano (str)

    Return :
    ---------
    data : dictionary with all information (dictionary)

    Version :
    -----------
    specification: Elie Goche (v.1 19/02/2022)
    implementation: Elie Goche, Younes Kouza, Youssef Fiher, Omar Ametjaou (v.1 25/02/2022)
    """
    data = {}
    list_ano_file = []
    list_element_list = []
    file = open(ano_file, "r+")
    for line in file.readlines():
        string = line
        characters = "\n"
        for x in range(len(characters)):
            string = string.replace(characters[x], "")
            list_ano_file.append(string)
    list_ano_file.remove("map:")
    list_ano_file.remove("werewolves:")
    list_ano_file.remove("foods:")
    for elem in list_ano_file:
        list_elem = elem.split(" ")
        list_element_list.append(list_elem)

    list_foods = []
    data_foods = {}
    list_werewolves = []
    data_werewolves = {}
    list_map = []

    for info in list_element_list:
        if len(info) == 2:
            list_map.append(info)
        if len(info) == 4:
            if info[3] in ["omega", "alpha", "normal"]:
                list_werewolves.append(info)
            elif info[2] in ["berries", "apples", "mice", "rabbits", "deers"]:
                list_foods.append(info)

    id_werewolves = 0
    id_foods = 0

    for list in list_werewolves:
        id_werewolves += 1
        data_werewolves["w" + str(id_werewolves)] = {"location": [int(list[1]), int(list[2])],
                                                     "type": list[3],
                                                     "type_ref": list[3],
                                                     "team": int(list[0]),
                                                     "previous_energy": 100,
                                                     "energy": 100,
                                                     "bonus": 0,
                                                     "pacified": False,
                                                     "nb_action": 0}

    for list in list_foods:
        id_foods += 1
        data_foods["f" + str(id_foods)] = {"location": [int(list[0]), int(list[1])],
                                           "type": list[2],
                                           "energy": int(list[3])}

    for list in list_map:
        data["map"] = [int(list[0]), int(list[1])]

    data["werewolves"] = data_werewolves
    data["foods"] = data_foods

    return data


def create_empty_map(map_size):
    """This function returns a dictionary with all information for each line in the map
    Parameters :
    ----------
    map_location : the size of the map (list)

    Return :
    ------
    data_map : dictionary with all information for each line in the map

    Version :
    -----------
    specification: Elie Goche (v.1 19/02/2022)
    implementation: Elie Goche, Younes Kouza (v.1 25/02/2022)
    """
    data_map = {}
    list = []
    for line in range(map_size[0] * 2 + 1):
        if line % 2 != 1:
            for rang in range(map_size[1] * 2 + 1):
                if rang % 2 != 1:
                    list.append("+")
                else:
                    list.append("--")
                data_map["l" + str(line)] = list
            list = []
        else:
            for rang in range(map_size[1] * 2 + 1):
                if rang % 2 != 1:
                    list.append("|")
                else:
                    list.append("  ")
                data_map["l" + str(line)] = list
            list = []
    return data_map


def place_werewolves(data, data_map, id, team, letter):
    """This function adds to the data_map the location of all werewolves in each line with their type and energy level
    Parameters:
    ----------
    data: dictionary of all information from the file.ano (dict)
    data_map: dictionary with all information for each line in the map (dict)
    id: the id of the werewolve (str)
    team: the team of the werewolve (int)
    letter: the type of the werewolve (A=alpha, O=omega, W=werewolve, H=humain) (str)

    Return:
    ------
    data_map: dictionary with all information for each line in the map (dict)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 25/03/2022)
    implementation: Elie Goche(v.1 05/03/2022)
    """
    if team == 1:
        if letter == "A":
            data_map["l" + str((data["werewolves"][id]["location"][0]) * 2 - 1)][
                (data["werewolves"][id]["location"][1]) * 2 - 1] = term.lightblue1(letter) + get_color_energy(data, id)
        else:
            if data['werewolves'][id]["energy"] <= 0:
                data['werewolves'][id]["energy"] = 0
                data['werewolves'][id]["type"] = "human"
                data_map["l" + str((data["werewolves"][id]["location"][0]) * 2 - 1)][
                    (data["werewolves"][id]["location"][1]) * 2 - 1] = term.lightblue1("H ")

            else:
                data_map["l" + str((data["werewolves"][id]["location"][0]) * 2 - 1)][
                    (data["werewolves"][id]["location"][1]) * 2 - 1] = term.lightblue1(letter) + get_color_energy(data,
                                                                                                                  id)
    else:
        if letter == "A":
            data_map["l" + str((data["werewolves"][id]["location"][0]) * 2 - 1)][
                (data["werewolves"][id]["location"][1]) * 2 - 1] = term.orangered(letter) + get_color_energy(data, id)
        else:
            if data['werewolves'][id]["energy"] <= 0:
                data['werewolves'][id]["energy"] = 0
                data['werewolves'][id]["type"] = "human"
                data_map["l" + str((data["werewolves"][id]["location"][0]) * 2 - 1)][
                    (data["werewolves"][id]["location"][1]) * 2 - 1] = term.orangered("H ")
            else:
                data_map["l" + str((data["werewolves"][id]["location"][0]) * 2 - 1)][
                    (data["werewolves"][id]["location"][1]) * 2 - 1] = term.orangered(letter) + get_color_energy(data,
                                                                                                                 id)
    return data_map


def place_foods(data, data_map, id, letter):
    """This function adds the location of all fruits in each line
    Parameters :
    ----------
    data : dictionary with all information (dict)
    data_map :dictionary with all information for each line in the map (dict)
    id : the id of the fruit (str)
    letter : the type of the fruit (str)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 25/03/2022)
    implementation: Elie Goche(v.1 05/03/2022)
    """

    data_map["l" + str(data["foods"][id]["location"][0] * 2 - 1)][
        (data["foods"][id]["location"][1]) * 2 - 1] = letter + get_color_energy(data, id)


def refresh_map(data, data_map):
    """This function refresh the map with all modification
    Parameters :
    -----------
    data : dictionary with all information (dict)
    data_map : dictionary with all information for each line in the map (dict)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 222/03/2022)
    implementation: Elie Goche, Younes Kouza(v.1 05/03/2022)
    """
    for id in data["foods"]:
        if data["foods"][id]["type"] == "berries":
            place_foods(data, data_map, id, "b")
        elif data["foods"][id]["type"] == "apples":
            place_foods(data, data_map, id, "a")
        elif data["foods"][id]["type"] == "mice":
            place_foods(data, data_map, id, "m")
        elif data["foods"][id]["type"] == "rabbits":
            place_foods(data, data_map, id, "r")
        else:
            place_foods(data, data_map, id, "d")

    for id in data["werewolves"]:
        add_bonus(data, id)
        team = data["werewolves"][id]['team']
        if data["werewolves"][id]["type"] == "alpha":
            place_werewolves(data, data_map, id, team, "A")
        elif data["werewolves"][id]["type"] == "omega":
            place_werewolves(data, data_map, id, team, "O")
        elif data["werewolves"][id]["type"] == "normal":
            place_werewolves(data, data_map, id, team, "W")
        else:
            place_werewolves(data, data_map, id, team, "H")


def show_map(data, data_map):
    """Show map in the terminal
    parameters :
    -----------
    data : dictionary with all information (dict)
    data_map : dictionary with all information for each line in the map (dict)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 25/03/2022)
    implementation: Younes Kouza (v.1 10/02/2022)
    """
    refresh_map(data, data_map)
    for line in data_map.values():
        print(*line, sep='')


def add_bonus(data, creature_id):
    """This function adds the bonus of werewolve in data dictionary
    Parameters:
    ----------
    data : dictionary with all information (dcit)
    creature_id : the id of the creature (str)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 21/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou(v.1 15/03/2022)
    """
    bonus = 0
    for werewolve_id in data['werewolves']:
        if get_creature_team(data, werewolve_id) == get_creature_team(data,
                                                                      creature_id) and werewolve_id != creature_id:
            if get_creature_type(data, werewolve_id) == 'normal':
                if get_distance(data, creature_id, werewolve_id) <= 2:
                    bonus += 10
            elif get_creature_type(data, werewolve_id) == 'alpha':
                if get_distance(data, creature_id, werewolve_id) <= 4:
                    bonus += 30
    data["werewolves"][creature_id]["bonus"] = bonus


def get_object_energy(data, object_id):
    """This function returns the object energy of the given object id
    Parameters:
    ----------
    data: dictionary with all information (dict)
    object_id: the id of the object (str)

    Return:
    -------
    energy: the energy of the creature

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 02/03/2022)

    """
    if 'w' in object_id:
        return data['werewolves'][object_id]['energy']
    elif 'f' in object_id:
        return data['foods'][object_id]['energy']


def get_creature_previous_energy(data, creature_id):
    """This function returns the previous_energy of the given creature id
    Parameters:
    ----------
    data: dictionary with all information (dict)
    object_id: the id of the creature (str)

    Return:
    ------
    previous_energy: the previous energy of the creature

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 05/03/2022)
    """
    previous_energy = data['werewolves'][creature_id]['previous_energy']
    return previous_energy


def get_color_energy(data, object_id):
    """Returns the color energy of the given object
    Parameters:
    ----------
    data: dictionary with all information (dict)
    object_id: the id of the object (str)

    Return:
    ------
    color: the color energy of the object

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche, Omar Ametjaou (v.1 12/03/2022)
    """
    if "w" in object_id:
        if data["werewolves"][object_id]["energy"] == 100:
            return term.darkgreen_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 90:
            return term.green3_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 80:
            return term.green_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 70:
            return term.greenyellow_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 60:
            return term.darkolivegreen1_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 50:
            return term.yellow2_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 40:
            return term.gold_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 30:
            return term.orange_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 20:
            return term.darkorange_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 10:
            return term.orangered_reverse(" ")
        elif data["werewolves"][object_id]["energy"] > 1:
            return term.red3_reverse(" ")
        else:
            return " "
    else:
        if data["foods"][object_id]["energy"] == 500:
            return term.darkgreen_reverse(" ")
        elif data["foods"][object_id]["energy"] > 450:
            return term.green3_reverse(" ")
        elif data["foods"][object_id]["energy"] > 350:
            return term.green_reverse(" ")
        elif data["foods"][object_id]["energy"] > 300:
            return term.greenyellow_reverse(" ")
        elif data["foods"][object_id]["energy"] > 250:
            return term.darkolivegreen1_reverse(" ")
        elif data["foods"][object_id]["energy"] > 200:
            return term.yellow2_reverse(" ")
        elif data["foods"][object_id]["energy"] > 150:
            return term.orange_reverse(" ")
        elif data["foods"][object_id]["energy"] > 100:
            return term.darkorange_reverse(" ")
        elif data["foods"][object_id]["energy"] > 50:
            return term.orangered_reverse(" ")
        elif data["foods"][object_id]["energy"] > 1:
            return term.red3_reverse(" ")
        else:
            return " "


def get_id_from_location(data, location):
    """This function returns the id of the creature from his location
    Parameters:
    ----------
    data: dictionary with all information (dict)
    location: the location of the creature (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche, Younes Kouza (v.1 05/03/2022)
    """
    for creature_id in data["werewolves"]:
        if data["werewolves"][creature_id]["location"] == location:
            return creature_id

    for food_id in data["foods"]:
        if data["foods"][food_id]["location"] == location:
            return food_id


def get_nearest_integer(n):
    """Returns the nearest integer of the given n
    Parameters:
    ----------
    n: number to get his nearest (int)

    Return:
    ------
    nearest_n: the nearest integer of the given n (int)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 05/03/2022)
    """
    if n % 1 >= 0.5:
        return int(n) + 1
    else:
        return int(n)


def get_creature_bonus(data, creature_id):
    """This function returns the creature bonus
    Parameters:
    ----------
    data: dictionary with all information (dict)
    creature_id: the id of the creature (str)

    Return:
    -------
    bonus: the bonus of the creature (int)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 05/03/2022)
    """
    return data["werewolves"][creature_id]["bonus"]


def get_creature_damage(data, creature_id):
    """This function returns the creature damage
    Parameters:
    ----------
    data: dictionary with all information (dict)
    creature_id: the id of the creature (str)

    Return:
    -------
    damage: the damage of the creature (int)

    Version :
    -----------
    specification: Omar Ametjaou, Youssef Fiher (v.1 22/03/2022)
    implementation: Omar Ametjaou, Youssef Fiher (v.1 05/03/2022)
    """
    damage = get_nearest_integer(1 / 10 * (get_object_energy(data, creature_id) + get_creature_bonus(data, creature_id)))
    return damage


def get_object_name(object_id):
    """This function returns the name of the object from the given object id
    Parameters:
    ----------
    object_id: the id of the object (str)

    Return:
    ------
    object_name = the name of the object ('werewolves' or 'foods') (str)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche (v.1 05/03/2022)
    """
    if 'w' in object_id:
        return 'werewolves'
    elif 'f' in object_id:
        return 'foods'


def get_object_location(data, object_id):
    """This function returns the location of the given object id
    Parameters:
    ----------
    data: dictionary with all information (dict)
    object_id: the id of the object (str)

    Return:
    ------
    location: the location of the object (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche (v.1 05/03/2022)
    """
    if 'w' in object_id:
        return data["werewolves"][object_id]["location"]
    elif 'f' in object_id:
        return data["foods"][object_id]["location"]


def get_distance(data, object1_id, object2_id):
    """this function returns the distance between two objects
    parameters :
    -----------
    data : dictionnary with all information
    object1_id : the first object
    object2_id : the second object

    Return :
    ---------
    distance : the distance between two objects

    Version :
    -----------
    specification: Omar Ametjaou, Youssef Fiher (v.1 22/03/2022)
    implementation: Omar Ametjaou, Youssef Fiher (v.1 05/03/2022)
    """
    r1 = data[get_object_name(object1_id)][object1_id]["location"][0]
    c1 = data[get_object_name(object1_id)][object1_id]['location'][1]
    r2 = data[get_object_name(object2_id)][object2_id]['location'][0]
    c2 = data[get_object_name(object2_id)][object2_id]['location'][1]
    return max(abs(r2 - r1), abs(c2 - c1))


def get_creature_team(data, creature_id):
    """This function returns the team of the given creature
    Parameters:
    ----------
    data: dictionary with all information (dict)
    creature_id: the id of the creature (str)

    Return:
    ------
    team: the team of the creature (int)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 05/03/2022)
    """
    if "w" in creature_id:
        return data["werewolves"][creature_id]["team"]


def get_creature_type_ref(data, creature_id):
    """This function returns the reference type of the given creature id
    Parameters:
    ----------
    data: dictionary with all information (dict)
    creature_id: the id of the creature (str)

    Return:
    ------
    type_ref: the reference type of the creature (int)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche (v.1 05/03/2022)
    """
    return data['werewolves'][creature_id]['type_ref']


def get_creature_type(data, creature_id):
    """This function returns the type of the given creature
    Parameters:
    ----------
    data: dictionary with all information (dict)
    creature_id: the id of the creature (str)

    Return:
    ------
    type: the type of the creature (int)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 05/03/2022)
    """
    return data['werewolves'][creature_id]['type']


def get_creature_nb_action(data, creature_id):
    """This function returns the number of actions of the given creature id
    Parameters:
    ----------
    data: dictionary with all information (dict)
    creature_id: the id of the creature (str)

    Return:
    ------
    nb_action: the number of actions of the creature (int)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche (v.1 05/03/2022)
    """
    return data['werewolves'][creature_id]['nb_action']


def set_pacify_false_for_all(data):
    """This function sets pacify False for all werewolves in data
    Parameter:
    ---------
    data: dictionary with all information (dict)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche (v.1 05/03/2022)
    """
    for id in data["werewolves"]:
        data["werewolves"][id]["pacified"] = False


def set_nb_action_to_0_for_all(data):
    """This function sets number actions to 0 for all werewolves in data
    Parameter:
    ---------
    data: dictionary with all information (dict)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche (v.1 05/03/2022)
    """
    for id in data["werewolves"]:
        data["werewolves"][id]["nb_action"] = 0


def get_instruction(data, data_map, list_instruction):
    """This function executes the instructions of the given list of instructions
    Parameters:
    -----------
    data: dictionary with all information (dict)
    data_map: dictionary with all information for each line in the map (dict)
    list_instruction: a list of instructions to be executed (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou, Younes Kouza, Elie Goche (v.1 05/03/2022)
    """
    set_pacify_false_for_all(data)
    set_nb_action_to_0_for_all(data)
    sorted_list_instruction = sort_instruction(list_instruction)
    move = "@"
    fight = "*"
    feed = "<"
    pacify = "pacify"
    for position_instruction in sorted_list_instruction:
        if pacify in position_instruction:
            int_list_position = manipulate_instruction(position_instruction, pacify)
            if get_creature_nb_action(data, get_id_from_location(data, int_list_position)) == 0:
                pacification(data, get_id_from_location(data, int_list_position))

        elif fight in position_instruction:
            int_list_new_position, int_list_old_position, sub_x, sub_y = manipulate_instruction(position_instruction,
                                                                                                fight)
            if get_id_from_location(data, int_list_old_position) != None:
                if get_creature_nb_action(data, get_id_from_location(data, int_list_old_position)) == 0:
                    if 0 < int_list_old_position[0] <= data["map"][0] and 0 < int_list_old_position[1] <= data["map"][
                        1] and 0 < int_list_new_position[0] <= data["map"][0] and \
                            0 < int_list_new_position[1] <= data["map"][1]:
                        if -1 <= sub_x <= 1 and -1 <= sub_y <= 1:
                            fight_creature(data, data_map, int_list_old_position, int_list_new_position)

        elif feed in position_instruction:
            int_list_new_position, int_list_old_position, sub_x, sub_y = manipulate_instruction(position_instruction,
                                                                                                feed)
            if get_id_from_location(data, int_list_old_position) != None:
                if get_creature_nb_action(data, get_id_from_location(data, int_list_old_position)) == 0:
                    if 0 < int_list_old_position[0] <= data["map"][0] and 0 < int_list_old_position[1] <= data["map"][
                        1] and 0 < int_list_new_position[0] <= data["map"][0] and \
                            0 < int_list_new_position[1] <= data["map"][1]:
                        if -1 <= sub_x <= 1 and -1 <= sub_y <= 1:
                            feed_creature(data, data_map, int_list_old_position, int_list_new_position)

        elif move in position_instruction:
            int_list_new_position, int_list_old_position, sub_x, sub_y = manipulate_instruction(position_instruction,
                                                                                                move)
            if get_id_from_location(data, int_list_old_position) != None:
                if get_creature_nb_action(data, get_id_from_location(data, int_list_old_position)) == 0:
                    if 0 < int_list_old_position[0] <= data["map"][0] and 0 < int_list_old_position[1] <= data["map"][
                        1] and 0 < int_list_new_position[0] <= data["map"][0] and \
                            0 < int_list_new_position[1] <= data["map"][1]:
                        if -1 <= sub_x <= 1 and -1 <= sub_y <= 1:
                            move_creature(data, data_map, int_list_old_position, int_list_new_position)


def sort_instruction(list_instruction):
    """This function sorts the list of instructions
    Parameter:
    ----------
    list_instruction: a list of instructions to sort (list)

    Return:
    ------
    sorted_list_instruction: a list of sorted instructions (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche (v.1 05/03/2022)
    """
    sorted_list_instruction = []
    for instruction in list_instruction:
        if "pacify" in instruction:
            sorted_list_instruction.append(instruction)
        if "*" in instruction:
            sorted_list_instruction.append(instruction)
        if "<" in instruction:
            sorted_list_instruction.append(instruction)
        if "@" in instruction:
            sorted_list_instruction.append(instruction)
    return sorted_list_instruction


def manipulate_instruction(position_instruction, symbol):
    if symbol == "@" or symbol == "*" or symbol == "<":
        final_position_instruction = position_instruction.replace(symbol, "")
        list_final_position_instruction = final_position_instruction.split(":")
        list_old_position = list_final_position_instruction[0].split("-")
        int_list_old_position = []
        for number in list_old_position:
            int_list_old_position.append(int(number))
        list_new_position = list_final_position_instruction[1].split("-")
        int_list_new_position = []
        for number in list_new_position:
            int_list_new_position.append(int(number))
        sub_x = int_list_old_position[0] - int_list_new_position[0]
        sub_y = int_list_old_position[1] - int_list_new_position[1]
        return int_list_new_position, int_list_old_position, sub_x, sub_y
    else:
        final_position_instruction = position_instruction.replace(":" + symbol, "")
        list_position = final_position_instruction.split("-")
        int_list_position = []
        for number in list_position:
            int_list_position.append(int(number))
        return int_list_position


def move_creature(data, data_map, int_list_old_position, int_list_new_position):
    """This function moves the creature in the given position
    Parameters:
    -----------
    data: dictionary with all information (dict)
    data_map: dictionary with all information for each line in the map (dict)
    int_list_old_position: the old position of the creature (list)
    int_list_new_position:  the new position of the creature (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche, Younes Kouza (v.1 05/03/2022)
    """
    if "w" in get_id_from_location(data, int_list_old_position):
        creature_id = get_id_from_location(data, int_list_old_position)
        if data_map["l" + str(int_list_old_position[0] * 2 - 1)][int_list_old_position[1] * 2 - 1] != "  ":
            if data_map["l" + str(int_list_new_position[0] * 2 - 1)][int_list_new_position[1] * 2 - 1] not in ["W ",
                                                                                                               "A ",
                                                                                                               "O ",
                                                                                                               "H "]:
                data_map["l" + str(int_list_old_position[0] * 2 - 1)][int_list_old_position[1] * 2 - 1] = "  "
                data["werewolves"][creature_id]["location"] = int_list_new_position
                data["werewolves"][creature_id]["nb_action"] += 1
                refresh_map(data, data_map)


def fight_creature(data, data_map, int_list_ally_position, int_list_ennemi_position):
    """Make two creature fight
    parameters :
    -----------
    data : dicitonary with all information (dict)
    data_map : dicitonary with map information for each line (dict)
    int_list_ally_position : the position of the ally (list)
    int_list_enemy_position : the position of the enemy (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Elie Goche, Younes Kouza (v.1 05/03/2022)
    """
    creature_ally_id = get_id_from_location(data, int_list_ally_position)
    creature_ennemi_id = get_id_from_location(data, int_list_ennemi_position)
    if data_map["l" + str(int_list_ally_position[0] * 2 - 1)][int_list_ally_position[1] * 2 - 1] not in ["  ", "a ",
                                                                                                         "b ", "m ",
                                                                                                         "r ", "d ",
                                                                                                         "H "] and \
            data_map["l" + str(int_list_ennemi_position[0] * 2 - 1)][int_list_ennemi_position[1] * 2 - 1] not in ["  ",
                                                                                                                  "a ",
                                                                                                                  "b ",
                                                                                                                  "m ",
                                                                                                                  "r ",
                                                                                                                  "d ",
                                                                                                                  "H "] and \
            data["werewolves"][creature_ally_id]["pacified"] == False:
        data['werewolves'][creature_ennemi_id]['energy'] -= get_creature_damage(data, creature_ally_id)
        data["werewolves"][creature_ally_id]["nb_action"] += 1


def feed_creature(data, data_map, int_list_creature_position, int_food_position):
    """Change the energies of the creature after eating a fruit
    parameters:
    -----------
    data : dictionary with all inforamtion (dict)
    data_map : dicitonary with map information for each line (dict)
    int_list_creature_position : the position of the creature (list)
    int_food_position : the position of the fruit (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 05/03/2022)
    """
    if int_list_creature_position != int_food_position:
        creature_id = get_id_from_location(data, int_list_creature_position)
        food_id = get_id_from_location(data, int_food_position)
        if data_map["l" + str(int_list_creature_position[0] * 2 - 1)][int_list_creature_position[1] * 2 - 1] not in [
            "  ",
            "a ",
            "b ",
            "m ",
            "r ",
            "d "] and \
                data_map["l" + str(int_food_position[0] * 2 - 1)][int_food_position[1] * 2 - 1] not in ["  ", "O ",
                                                                                                        "A ",
                                                                                                        "W ",
                                                                                                        "H "]:
            if get_object_energy(data, creature_id) < 100:
                if get_object_energy(data, creature_id) + get_object_energy(data, food_id) <= 100:
                    data["werewolves"][creature_id]["energy"] += get_object_energy(data, food_id)
                    data["werewolves"][creature_id]["type"] = get_creature_type_ref(data, creature_id)
                    data["foods"][food_id]["energy"] = 0
                    data_map["l" + str(int_food_position[0] * 2 - 1)][int_food_position[1] * 2 - 1] = "  "
                    del data["foods"][food_id]
                    data["werewolves"][creature_id]["nb_action"] += 1
                else:
                    data["foods"][food_id]["energy"] -= (100 - get_object_energy(data, creature_id))
                    data["werewolves"][creature_id]["energy"] = 100
                    data["werewolves"][creature_id]["type"] = get_creature_type_ref(data, creature_id)
                    data["werewolves"][creature_id]["nb_action"] += 1


def pacification(data, omega_id):
    """Cancels all attacks in a certain area from omega
    Parameters :
    -----------
    data : dicitonary with all information (dict)
    omega_id : the location of omega (list)

    Version :
    -----------
    specification: Youssef Fiher, Omar Ametjaou, Elie Goche (v.1 22/03/2022)
    implementation: Youssef Fiher, Omar Ametjaou (v.1 05/03/2022)
    """
    if get_creature_type(data, omega_id) == 'omega':
        residual_energy_omega = get_object_energy(data, omega_id)
        if residual_energy_omega > 40:
            data['werewolves'][omega_id]['energy'] -= 40
            data["werewolves"][omega_id]["nb_action"] += 1
            for creature_id in data['werewolves']:
                if get_creature_type(data, creature_id) == 'normal' or get_creature_type(data, creature_id) == 'alpha':
                    if get_distance(data, omega_id, creature_id) <= 6:
                        data["werewolves"][creature_id]["pacified"] = True


def check_if_good_team(data, instruction, team):
    """This function delete the instruction when the team doesn't correspond with the player's team
    Parameter:
    ----------
    data: data of all information (dictionary)
    instruction: instruction that the player (or AI) gives (list)
    team : team of the player (int)

    Return:
    -------
    list_valid_team_instruction: a list of valid team instructions (list)

    Version:
    ---------
    specification: Elie Goche (v.1 28/03/2022)
    implementation: Elie Goche (v.1 25/03/2022)
    """
    list_instruction = instruction.split(" ")
    move = "@"
    fight = "*"
    feed = "<"
    pacify = "pacify"
    list_valid_team_instruction = []
    for position_instruction in list_instruction:
        if pacify in position_instruction:
            int_list_position = manipulate_instruction(position_instruction, pacify)
            if get_id_from_location(data, int_list_position) != None:
                if get_creature_team(data, get_id_from_location(data, int_list_position)) == team:
                    list_valid_team_instruction.append(position_instruction)
        elif fight in position_instruction:
            int_list_new_position, int_list_old_position, sub_x, sub_y = manipulate_instruction(position_instruction,
                                                                                                fight)
            if get_id_from_location(data, int_list_old_position) != None:
                if get_creature_team(data, get_id_from_location(data, int_list_old_position)) == team:
                    list_valid_team_instruction.append(position_instruction)
        elif feed in position_instruction:
            int_list_new_position, int_list_old_position, sub_x, sub_y = manipulate_instruction(position_instruction,
                                                                                                feed)
            if get_id_from_location(data, int_list_old_position) != None:
                if get_creature_team(data, get_id_from_location(data, int_list_old_position)) == team:
                    list_valid_team_instruction.append(position_instruction)
        elif move in position_instruction:
            int_list_new_position, int_list_old_position, sub_x, sub_y = manipulate_instruction(position_instruction,
                                                                                                move)
            if get_id_from_location(data, int_list_old_position) != None:
                if get_creature_team(data, get_id_from_location(data, int_list_old_position)) == team:
                    list_valid_team_instruction.append(position_instruction)
    return list_valid_team_instruction


def get_AI_orders(data, data_map, team):
    """This function gives is the basic algorithm of the AI. The AI give randomly instructions
    Parameter:
    ----------
    data: data of all information (dictionary)
    team : team of the player (int)

    Return:
    -------
    all_move_instruction[:-1]: all move instructions gived by the AI (str)

    Version:
    ---------
    specification: Elie Goche (v.1 28/03/2022)
    implementation: Elie Goche (v.1 25/03/2022)
    """
    list_move_instruction = []
    for creature_id in data["werewolves"]:
        if get_creature_team(data, creature_id) == team:
            creature_location = get_object_location(data, creature_id)
            if get_creature_type(data, creature_id) in ["normal", "omega"]:
                if get_object_energy(data, creature_id) >= 30:
                    for alpha_id in data["werewolves"]:
                        if get_creature_team(data, alpha_id) == team and get_creature_type(data, alpha_id) == "alpha":
                            alpha_location = get_object_location(data, alpha_id)
                            for alpha_team2_id in data["werewolves"]:
                                if get_creature_team(data, alpha_team2_id) != team and get_creature_type(data,
                                                                                                         alpha_team2_id) == "alpha":
                                    alpha_team2_location = get_object_location(data, alpha_team2_id)
                                    if get_distance(data, alpha_id, alpha_team2_id) > 5:
                                        if get_distance(data, creature_id, alpha_id) > 2:
                                            object1_to_object2(data, data_map, creature_location, alpha_location,
                                                               list_move_instruction, "@")
                                        elif get_distance(data, creature_id, alpha_id) < 3:
                                            object1_move_reverse_to_object2(data, data_map, creature_location,
                                                                            alpha_location, list_move_instruction)
                                        else:
                                            for creature_enemy_id in data["werewolves"]:
                                                if get_creature_team(data, creature_enemy_id) != team:
                                                    if get_distance(data, creature_id, creature_enemy_id) == 1:
                                                        creature_enemy_location = get_object_location(data,
                                                                                                      creature_enemy_id)
                                                        object1_to_object2(data, data_map, creature_location,
                                                                           creature_enemy_location,
                                                                           list_move_instruction, "*")

                                    else:
                                        for creature_enemy_id in data["werewolves"]:
                                            if get_creature_team(data, creature_enemy_id) != team:
                                                if get_distance(data, creature_id, creature_enemy_id) == 1:
                                                    creature_enemy_location = get_object_location(data,
                                                                                                  creature_enemy_id)
                                                    object1_to_object2(data, data_map, creature_location,
                                                                       creature_enemy_location, list_move_instruction,
                                                                       "*")
                                        object1_to_object2(data, data_map, creature_location, alpha_team2_location,
                                                           list_move_instruction, "@")

                else:
                    if data["foods"] != {}:
                        for food_id in data["foods"]:
                            food_location = get_object_location(data, food_id)
                            if get_distance(data, creature_id, food_id) > 1:
                                object1_to_object2(data, data_map, creature_location, food_location,
                                                   list_move_instruction, "@")
                            else:
                                object1_to_object2(data, data_map, creature_location, food_location,
                                                   list_move_instruction, "<")

                    else:
                        for creature_enemy_id in data["werewolves"]:
                            if get_creature_team(data, creature_enemy_id) != team:
                                if get_distance(data, creature_id, creature_enemy_id) == 1:
                                    creature_enemy_location = get_object_location(data, creature_enemy_id)
                                    object1_to_object2(data, data_map, creature_location,
                                                       creature_enemy_location, list_move_instruction, "*")


            elif get_creature_type(data, creature_id) == "human":
                if data["foods"] == {}:
                    for alpha_id in data["werewolves"]:
                        if get_creature_team(data, alpha_id) == team and get_creature_type(data, alpha_id) == "alpha":
                            alpha_location = get_object_location(data, alpha_id)
                            object1_move_reverse_to_object2(data, data_map, creature_location, alpha_location,
                                                            list_move_instruction)
                else:
                    for food_id in data["foods"]:
                        food_location = get_object_location(data, food_id)
                        if get_distance(data, creature_id, food_id) > 1:
                            object1_to_object2(data, data_map, creature_location, food_location,
                                               list_move_instruction, "@")
                        else:
                            object1_to_object2(data, data_map, creature_location, food_location,
                                               list_move_instruction, "<")
            else:
                if get_object_energy(data, creature_id) >= 50:
                    for alpha_team2_id in data["werewolves"]:
                        if get_creature_team(data, alpha_team2_id) != team and get_creature_type(data,
                                                                                                 alpha_team2_id) == "alpha":
                            alpha_team2_location = get_object_location(data, alpha_team2_id)
                            if get_distance(data, creature_id, alpha_team2_id) > 5:
                                object1_to_object2(data, data_map, creature_location, alpha_team2_location,
                                                   list_move_instruction, "@")
                            elif get_distance(data, creature_id, alpha_team2_id) < 4:
                                object1_move_reverse_to_object2(data, data_map, creature_location, alpha_team2_location,
                                                                list_move_instruction)
                            else:
                                for creature_enemy_id in data["werewolves"]:
                                    if get_creature_team(data, creature_enemy_id) != team:
                                        if get_distance(data, creature_id, creature_enemy_id) == 1:
                                            creature_enemy_location = get_object_location(data, creature_enemy_id)
                                            object1_to_object2(data, data_map, creature_location,
                                                               creature_enemy_location, list_move_instruction, "*")
                else:
                    for omega_id in data["werewolves"]:
                        if get_creature_team(data, omega_id) == team and get_creature_type(data, omega_id) == "omega":
                            omega_location = get_object_location(data, omega_id)
                            object1_to_object2(data, data_map, omega_location, None, list_move_instruction, "pacify")

                    if data["foods"] == {}:
                        for alpha_team2_id in data["werewolves"]:
                            if get_creature_team(data, alpha_team2_id) != team and get_creature_type(data,
                                                                                                     alpha_team2_id) == "alpha":
                                alpha_team2_location = get_object_location(data, alpha_team2_id)
                                object1_to_object2(data, data_map, creature_location,
                                                   alpha_team2_location, list_move_instruction, "@")
                    else:
                        for food_id in data["foods"]:
                            food_location = get_object_location(data, food_id)
                            if get_distance(data, creature_id, food_id) > 1:
                                object1_to_object2(data, data_map, creature_location, food_location,
                                                   list_move_instruction, "@")
                            else:
                                object1_to_object2(data, data_map, creature_location, food_location,
                                                   list_move_instruction, "<")

    all_move_instruction = ""
    for move_instruction in list_move_instruction:
        all_move_instruction += move_instruction + " "
    return all_move_instruction[:-1]


def object1_to_object2(data, data_map, object1_location, object2location, list_move_instruction, action):
    """This function  of AI. makes the wolve moves into the direction of an other object 
    Parameter:
    ----------
    data: data of all information (dictionary)
    data_map: dictionary with all information for each line in the map (dict)
    object1_location: the location of the first object (list)
    object2location: the location of the second object (list)
    list_move_instruction: list of instruction to be executed (list)
    action: move or attack or feed or pacify(str) 
    version :
    ---------
    specification: Youssef Fiher,Omar Ametjaou
    implementation:Youssef Fiher,Omar Ametjaou, Elie Goche 
    """
    if action == "@":
        # move down-right
        if object1_location[0] < object2location[0] and object1_location[1] < \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, +1, +1, 5)
            list_move_instruction.append(order)
        # move top-left
        elif object1_location[0] > object2location[0] and object1_location[1] > \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, -1, -1, 5)
            list_move_instruction.append(order)
        # move down-left
        elif object1_location[0] < object2location[0] and object1_location[1] > \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, +1, -1, 5)
            list_move_instruction.append(order)
        # move top-right
        elif object1_location[0] > object2location[0] and object1_location[1] < \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, -1, +1, 5)
            list_move_instruction.append(order)
        # move-right
        elif object1_location[0] == object2location[0] and object1_location[1] < \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, 0, +1, 5)
            list_move_instruction.append(order)
        # move left
        elif object1_location[0] == object2location[0] and object1_location[1] > \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, 0, -1, 5)
            list_move_instruction.append(order)
        # move down
        elif object1_location[0] < object2location[0] and object1_location[1] == \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, +1, 0, 5)
            list_move_instruction.append(order)
        # move top
        elif object1_location[0] > object2location[0] and object1_location[1] == \
                object2location[1]:
            order = AI_move_direction(data, data_map, object1_location, -1, 0, 5)
            list_move_instruction.append(order)
    elif action == "*":
        list_move_instruction.append(
            str(object1_location[0]) + "-" + str(
                object1_location[1]) + ":*" + str(
                object2location[0]) + "-" + str(object2location[1]))
    elif action == "<":
        list_move_instruction.append(
            str(object1_location[0]) + "-" + str(
                object1_location[1]) + ":<" + str(
                object2location[0]) + "-" + str(object2location[1]))
    elif action == "pacify":
        list_move_instruction.append(str(object1_location[0]) + "-" + str(object1_location[1]) + ":pacify")


def object1_move_reverse_to_object2(data, data_map, object1_location, object2location, list_move_instruction):
    """This function  of AI. makes the wolve moves into the opposite direction of the other object 
    Parameter:
    ----------
    data: data of all information (dictionary)
    data_map: dictionary with all information for each line in the map (dict)
    object1_location: the location of the first object (list)
    object2location: the location of the second object (list)
    list_move_instruction: list of instruction to be executed (list)
    Version :
    ---------
    specification: Youssef Fiher,Omar Ametjaou
    implementation:Youssef Fiher,Omar Ametjaou, Elie Goche 
    
    """
    # move down-right
    if object1_location[0] > object2location[0] and object1_location[1] > \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, +1, +1, 5)
        list_move_instruction.append(order)
    # move top-left
    elif object1_location[0] < object2location[0] and object1_location[1] < \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, -1, -1, 5)
        list_move_instruction.append(order)
    # move down-left
    elif object1_location[0] > object2location[0] and object1_location[1] < \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, +1, -1, 5)
        list_move_instruction.append(order)
    # move top-right
    elif object1_location[0] < object2location[0] and object1_location[1] > \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, -1, +1, 5)
        list_move_instruction.append(order)
    # move-right
    elif object1_location[0] == object2location[0] and object1_location[1] > \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, 0, +1, 5)
        list_move_instruction.append(order)
    # move left
    elif object1_location[0] == object2location[0] and object1_location[1] < \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, 0, -1, 5)
        list_move_instruction.append(order)
    # move down
    elif object1_location[0] > object2location[0] and object1_location[1] == \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, +1, 0, 5)
        list_move_instruction.append(order)
    # move top
    elif object1_location[0] < object2location[0] and object1_location[1] == \
            object2location[1]:
        order = AI_move_direction(data, data_map, object1_location, -1, 0, 5)
        list_move_instruction.append(order)


def AI_move_direction(data, data_map, location, y_move, x_move, nb_retry):
    if nb_retry == 0:
        return str(location[0]) + "-" + str(location[1]) + ":@" + str(location[0] + y_move) + "-" + str(
            location[1] + x_move)
    else:
        if data_map["l" + str(check_out_of_map(data, 1, location[0] + y_move) * 2 - 1)][
            check_out_of_map(data, 0, location[1] + x_move) * 2 - 1] == "  ":
            return str(location[0]) + "-" + str(location[1]) + ":@" + str(location[0] + y_move) + "-" + str(
                location[1] + x_move)
        else:
            y_move = random.randint(-1, 1)
            x_move = random.randint(-1, 1)
            return AI_move_direction(data, data_map, location, y_move, x_move, nb_retry - 1)


def check_out_of_map(data, x_y, number):
    if number < 1:
        return 1
    elif number > data["map"][x_y]:
        return data["map"][x_y]
    else:
        return number


# main function
def play_game(map_path, group_1, type_1, group_2, type_2):
    """Play a game.

    Parameters
    ----------
    map_path: path of map file (str)
    group_1: group of player 1 (int)
    type_1: type of player 1 (str)
    group_2: group of player 2 (int)
    type_2: type of player 2 (str)

    Notes
    -----
    Player type is either 'human', 'AI' or 'remote'.

    If there is an external referee, set group id to 0 for remote player.

    """
    data = extract_ano_file(map_path)
    data_map = create_empty_map(data["map"])
    game_over = False
    nb_round = 0
    nb_round_without_fight = -1
    # create connection, if necessary
    if type_1 == 'remote':
        connection = create_connection(group_2, group_1)
    elif type_2 == 'remote':
        connection = create_connection(group_1, group_2)

    while game_over == False:
        nb_round += 1
        nb_round_without_fight += 1
        print(term.home + term.clear)
        show_map(data, data_map)
        print("\nRound :", nb_round)
        print("\nRound without fight :", nb_round_without_fight)

        for creature_id in data["werewolves"]:
            if get_creature_team(data, creature_id) == 1 and get_creature_type(data,
                                                                               creature_id) == "alpha" and get_object_energy(
                data, creature_id) <= 0:
                game_over = True
                print("team 1 loose")
            elif get_creature_team(data, creature_id) == 2 and get_creature_type(data,
                                                                                 creature_id) == "alpha" and get_object_energy(
                data, creature_id) <= 0:
                game_over = True
                print("team 2 loose")

        for creature_id in data["werewolves"]:
            if get_object_energy(data, creature_id) != get_creature_previous_energy(data, creature_id):
                nb_round_without_fight = 0
                data["werewolves"][creature_id]["previous_energy"] = get_object_energy(data, creature_id)

        if nb_round_without_fight == 200:
            energy_team1 = 0
            energy_team2 = 0
            for creature_id in data["werewolves"]:
                if get_creature_team(data, creature_id) == 1:
                    energy_team1 += get_object_energy(data, creature_id)
                else:
                    energy_team2 += get_object_energy(data, creature_id)
            if energy_team1 > energy_team2:
                print("Team 1 win")
                game_over = True
            elif energy_team1 > energy_team2:
                print("Team 2 win")
                game_over = True
            else:
                print("Egality")
                game_over = True

        if game_over != True:

            if type_1 == "human":
                instruction_team_1 = input("TEAM 1: Pls give the instruction ")
                list_valid_team1_instruction = check_if_good_team(data, instruction_team_1, 1)
                if type_2 == 'remote':
                    notify_remote_orders(connection, instruction_team_1)
            elif type_1 == "AI":
                instruction_team_1 = get_AI_orders(data, data_map, 1)
                list_valid_team1_instruction = check_if_good_team(data, instruction_team_1, 1)
                if type_2 == 'remote':
                    notify_remote_orders(connection, instruction_team_1)
            elif type_1 == 'remote':
                instruction_team_1 = get_remote_orders(connection)
                list_valid_team1_instruction = check_if_good_team(data, instruction_team_1, 1)

            if type_2 == "human":
                instruction_team_2 = input("TEAM 2: Pls give the instruction ")
                list_valid_team2_instruction = check_if_good_team(data, instruction_team_2, 2)
                if type_1 == 'remote':
                    notify_remote_orders(connection, instruction_team_2)
            elif type_2 == "AI":
                instruction_team_2 = get_AI_orders(data, data_map, 2)
                list_valid_team2_instruction = check_if_good_team(data, instruction_team_2, 2)
                if type_1 == 'remote':
                    notify_remote_orders(connection, instruction_team_2)
            elif type_2 == 'remote':
                instruction_team_2 = get_remote_orders(connection)
                list_valid_team2_instruction = check_if_good_team(data, instruction_team_2, 1)
            get_instruction(data, data_map, list_valid_team1_instruction + list_valid_team2_instruction)
        time.sleep(0.2)


play_game('file.ano', 36, 'AI', 27, 'AI')

