
def struct_data():
    infoplayer1 = {}
    infoplayer2 = {}
    map = {}
    infofoods = {}
    fh = open("file.ano", "r")
    lines = fh.readlines()
    cpt = 0

    infoplayer1["normal"] = []
    infoplayer2["normal"] = []
    infofoods["berries"] = []
    infofoods["apples"] = []
    infofoods["nice"] = []
    infofoods["rabbits"] = []
    infofoods["deers"] = []
    map["maps"] = []

    for line in lines:
        data = line.split()

        for elmt in data:

            if data[0] == '1' and 1 <= cpt <= 150:
                if data[3] == "alpha":
                    infoplayer1["alpha"] = [int(data[1]), int(data[2])]
                if data[3] == "omega":
                    infoplayer1["omega"] = [int(data[1]), int(data[2])]
                if data[3] == "normal":
                    infoplayer1["normal"] += [[int(data[1]), int(data[2])]]
            if data[0] == "2":
                if data[3] == "alpha":
                    infoplayer2["alpha"] = [int(data[1]), int(data[2])]
                if data[3] == "omega":
                    infoplayer2["omega"] = [int(data[1]), int(data[2])]
                if data[3] == "normal":
                    infoplayer2["normal"] += [[int(data[1]), int(data[2])]]
        cpt += 1
    for line in lines:
        data = line.split()
        if (data[0] == "4" and data[1] == "4") or (data[0] == "4" and data[1] == "5") or (
                data[0] == "5" and data[1] == "4") or data[0] == "5" and data[1] == "5" or (
                data[0] == "16" and data[1] == "16") or (data[0] == "16" and data[1] == "17") or (
                data[0] == "17" and data[1] == "16") or (data[0] == "17" and data[1] == "17"):
            infofoods["berries"] += [[int(data[0]), int(data[1]), int(data[3])]]
        if (data[0] == "1" and data[1] == "4") or (data[0] == "1" and data[1] == "5") or (
                data[0] == "20" and data[1] == "16") or (data[0] == "20" and data[1] == "17"):
            infofoods["apples"] += [[int(data[0]), int(data[1]), int(data[3])]]
        if (data[0] == "4" and data[1] == "1") or (data[0] == "5" and data[1] == "1") or (
                data[0] == "16" and data[1] == "20") or (data[0] == "17" and data[1] == "20"):
            infofoods["nice"] += [[int(data[0]), int(data[1]), int(data[3])]]
        if (data[0] == "5" and data[1] == "7") or (data[0] == "16" and data[1] == "14"):
            infofoods["rabbits"] += [[int(data[0]), int(data[1]), int(data[3])]]
        if (data[0] == "7" and data[1] == "5") or (data[0] == "14" and data[1] == "16"):
            infofoods["deers"] += [[int(data[0]), int(data[1]), int(data[3])]]
        if (data[0] == "20") and (data[1] == "20"):
            map["maps"] = [[int(data[0]), int(data[1])]]

    return infoplayer1, infoplayer2, infofoods, map


infoplayer1, infoplayer2, infofoods, map = struct_data()
col_data = map["maps"][0][0]
row_data = map["maps"][0][1]

normal_team1_raw = infoplayer1["normal"]
normal_team1 = []
for i in normal_team1_raw:
    if i not in normal_team1:
        normal_team1.append(i)
infoplayer1["normal"] = normal_team1
normal_team2_raw = infoplayer2["normal"]
normal_team2 = []
for i in normal_team2_raw:
    if i not in normal_team2:
        normal_team2.append(i)
infoplayer2["normal"] = normal_team2

dict_team1 = {}

for j in range(len(infoplayer1["normal"])):
    dict_team1[(infoplayer1["normal"][j][0], infoplayer1["normal"][j][1])] = ["normal", 100]
    dict_team1[(infoplayer1["alpha"][0], infoplayer1["alpha"][1])] = ["alpha", 100]
    dict_team1[(infoplayer1["omega"][0], infoplayer1["omega"][1])] = ["omega", 100]
    team1 = dict_team1

dict_team2 = {}

for j in range(len(infoplayer2["normal"])):
    dict_team2[(infoplayer2["normal"][j][0], infoplayer2["normal"][j][1])] = ["normal", 100]
    dict_team2[(infoplayer2["alpha"][0], infoplayer2["alpha"][1])] = ["alpha", 100]
    dict_team2[(infoplayer2["omega"][0], infoplayer2["omega"][1])] = ["omega", 100]
    team2 = dict_team2

dict_foods = {}
for j in range(len(infofoods["berries"])):
    dict_foods[(infofoods["berries"][j][0], infofoods["berries"][j][1])] = \
        ["berries", infofoods["berries"][j][2]]
    for j in range(len(infofoods["apples"])):
        dict_foods[(infofoods["apples"][j][0], infofoods["apples"][j][1])] = \
            ["apples", infofoods["apples"][j][2]]
        for j in range(len(infofoods["nice"])):
            dict_foods[(infofoods["nice"][j][0], infofoods["nice"][j][1])] = \
                ["nice", infofoods["nice"][j][2]]
            for j in range(len(infofoods["rabbits"])):
                dict_foods[(infofoods["rabbits"][j][0], infofoods["rabbits"][j][1])] = \
                    ["rabbits", infofoods["rabbits"][j][2]]
                for j in range(len(infofoods["deers"])):
                    dict_foods[(infofoods["deers"][j][0], infofoods["deers"][j][1])] = \
                        ["deers", infofoods["deers"][j][2]]
                foods = dict_foods
get_game_dict = {"Map": map["maps"], "WEREWOLVES": {"TEAM_1": team1, "TEAM_2": team2}, "FOODS": foods}

print(get_game_dict)

take = input("entre la syntaxe de votre ordres\n")


def ordres(ordre_joueur=take):
    """ Recupère la syntax globale d'ordre donnée par le joueur et fait des splits sur l'espace ensuite sur le :* et sur le -

  Paramètres:
  __________
  ordre: ordre du joueur (list)

  returns
  _______
  list_ordre: liste contenant les ordres(dict)

  version
  _______
  specification: DJUIDEU Jason (v.1 19/02/22)
  implementation:Djuideu jason,Kenfak tresor,Daniel Efame mengur (v.1 18/03/22)
"""
    deplacement = []
    attacque = []
    pacify = []
    manger = []

    decoupage = ordre_joueur.split()
    for ordre in decoupage:
        if "@" in ordre:
            take1 = ordre.split(":@")
            coordonner1 = take1[0].split("-")
            coordonner2 = take1[1].split("-")
            coord1 = int(coordonner1[0])
            coord2 = int(coordonner1[1])
            depart = (coord1, coord2)
            coord3 = int(coordonner2[0])
            coord4 = int(coordonner2[1])
            arriver = (coord3, coord4)
            deplacement.append([depart, arriver])
        if "*" in ordre:
            take1 = ordre.split(":*")
            coordonner1 = take1[0].split("-")
            coordonner2 = take1[1].split("-")
            coord1 = int(coordonner1[0])
            coord2 = int(coordonner1[1])
            attaquant = (coord1, coord2)
            coord3 = int(coordonner2[0])
            coord4 = int(coordonner2[1])
            attaquer = (coord3, coord4)
            attacque.append([attaquant, attaquer])
        if "<" in ordre:
            take1 = ordre.split(":<")
            coordonner1 = take1[0].split("-")
            coordonner2 = take1[1].split("-")
            coord1 = int(coordonner1[0])
            coord2 = int(coordonner1[1])
            mangeur = (coord1, coord2)
            coord3 = int(coordonner2[0])
            coord4 = int(coordonner2[1])
            proie = (coord3, coord4)
            manger.append([mangeur, proie])
        if "pacify" in ordre:
            take1 = ordre.split(":pacify")
            coordonner1 = take1[0].split("-")
            coord1 = int(coordonner1[0])
            coord2 = int(coordonner1[1])
            imobile = (coord1, coord2)
            pacify.append(imobile)
    return deplacement, attacque, manger, pacify


ordre = ordres()
ordre_depla = ordre[0]
ordre_attack = ordre[1]
ordre_manger = ordre[2]
ordre_pacifier = ordre[3]


def verification(verifier_ordre=ordres()):
    """ parcourt les élements de la liste d'ordre et
      appellle la fonction correspondante pour l'éxecuition d'un ordre précis

  Paramètres:
  __________
  verifier_ordre:ordre du joueur

  returns
  _______
  pas de return

  version
  _______
  specification: Djuideu jason (v.1 19/02/22)
  implementation: implementation:Kenfak tresor (v.1 20/03/22)

"""
    verification_ordre_deplacement = verifier_ordre[0]
    verification_ordre_attack = verifier_ordre[1]
    verification_ordre_manger = verifier_ordre[2]
    verification_ordre_pacify = verifier_ordre[3]
    # mettres les donneur d'ordre dans une liste
    verification_final = []
    if verification_ordre_deplacement != []:
        for i in range(len(verification_ordre_deplacement)):
            verification_final.append(verification_ordre_deplacement[i][0])
    if verification_ordre_attack != []:
        for i in range(len(verification_ordre_attack)):
            verification_final.append(verification_ordre_attack[i][0])
    if verification_ordre_manger != []:
        for i in range(len(verification_ordre_manger)):
            verification_final.append(verification_ordre_manger[i][0])
    if verification_ordre_pacify != []:
        for i in range(len(verification_ordre_pacify)):
            verification_final.append(verification_ordre_pacify[i])
    # Verification du message
    cpt = 0
    verification = verification_final

    while verification != []:
        membre = verification[0]
        del verification[0]
        if membre in verification:
            cpt = cpt + 1
    if cpt > 0:
        return 0
    else:
        return 1


def deplacement(ordre_deplacement=ordre_depla, dictionnaire=get_game_dict, verify=verification()):
    """ Réalise le déplacement d'un joueur d'une case à une autre

  Paramètres:
  __________
  ordre_deplacement: ordre pour effectuer un deplacement(list)
  dictionnaire: dictionnaire de depart(dict)
  verify: verife si un ordre est correct(int)

  returns
  _______
  dictionnaire: dictionnaire comportant les changement effectuer sur le deplacement(dict)

  version
  _______
  specification:  Daniel Efame mengue  (v.1 19/02/22)
  implementation: Daniel Efame mengur (v.1 21/03/22)
  """
    if verify != 0:
        if ordre_deplacement != []:
            for deplacer in ordre_deplacement:
                deplacer1 = deplacer[0]
                deplacer2 = deplacer[1]
                x = deplacer1[0]
                y = deplacer1[1]
                w = deplacer2[0]
                z = deplacer2[1]
                distance = max(abs(w - x), abs(z - y))

                if distance == 1 and deplacer2 >= (1, 1) and deplacer2 <= (20, 20):
                    werewolves = dictionnaire["WEREWOLVES"]
                    joueur1 = werewolves["TEAM_1"]
                    joueur2 = werewolves["TEAM_2"]
                    if (deplacer1 in joueur1 or deplacer1 in joueur2) and (
                            deplacer2 not in joueur1 and deplacer2 not in joueur2):
                        if deplacer1 in joueur1:
                            dictionnaire["WEREWOLVES"]["TEAM_1"][deplacer2] = \
                            dictionnaire["WEREWOLVES"]["TEAM_1"][deplacer1]
                            del dictionnaire["WEREWOLVES"]["TEAM_1"][deplacer1]
                        elif deplacer1 in joueur2:
                            dictionnaire["WEREWOLVES"]["TEAM_2"][deplacer2] = \
                            dictionnaire["WEREWOLVES"]["TEAM_2"][deplacer1]
                            del dictionnaire["WEREWOLVES"]["TEAM_2"][deplacer1]
                        else:
                            raise ValueError("ce deplacement ne se peux pas")
                else:
                    raise ValueError("la distance entre ces deux points ne sont pas favorable")
        return dictionnaire
    else:
        raise ValueError("un wolf ne peut recevoir qu'un seul ordre")


def pacification(ordre_pacification=ordre_pacifier, dictionnaire=deplacement()):
    """ Pacifie tous les loups à une certaine distance de l'oméga

  Paramètres:
  __________
  ordre_pacification: ordre de pacification
  dictionnaire:qu'a retourner deplacement

  returns
  _______
  dictionnaire: comportant les modifications effectuer sur la pacification
  liste_pacifier: liste de tous les loups qui ont été pacifiés (list)

  version
  _______
  specification: Daniel Efame mengue  (v.1 19/02/22)
  implementation:Daniel Efame mengur (v.1 21/03/22)

"""
    liste_pacifier = []
    if ordre_pacification != []:

        for ordre_pacif in ordre_pacification:

            x = ordre_pacif[0]
            y = ordre_pacif[1]
            werewolves = dictionnaire["WEREWOLVES"]
            joueur1 = werewolves["TEAM_1"]
            joueur2 = werewolves["TEAM_2"]
            if ordre_pacif in joueur1 or ordre_pacif in joueur2:
                if ordre_pacif in joueur1 and dictionnaire["WEREWOLVES"]["TEAM_1"][ordre_pacif][1] >= 40 and \
                        dictionnaire["WEREWOLVES"]["TEAM_1"][ordre_pacif][0] == 'omega':
                    dictionnaire["WEREWOLVES"]["TEAM_1"][ordre_pacif][1] = \
                    dictionnaire["WEREWOLVES"]["TEAM_1"][ordre_pacif][1] - 40
                    for position in joueur2:
                        w = position[0]
                        z = position[1]
                        distance = max(abs(z - w), abs(y - x))
                        if position != ordre_pacif and distance <= 6:
                            liste_pacifier.append(position)
                elif ordre_pacif in joueur2 and dictionnaire["WEREWOLVES"]["TEAM_2"][ordre_pacif][1] >= 40 and \
                        dictionnaire["WEREWOLVES"]["TEAM_2"][ordre_pacif][0] == 'omega':

                    dictionnaire["WEREWOLVES"]["TEAM_2"][ordre_pacif][1] = \
                    dictionnaire["WEREWOLVES"]["TEAM_2"][ordre_pacif][1] - 40
                    for position in joueur1:
                        w = position[0]
                        z = position[1]
                        distance = max(abs(w - x), abs(z - y))
                        if position != ordre_pacif and distance <= 6:
                            liste_pacifier.append(position)
                else:
                    raise ValueError("les joueur autre que l' omega ne peuvent pas pacifier")
    return dictionnaire, liste_pacifier


def attack(ordre_attacque=ordre_attack, dico=pacification()):

    """ Réalise l'attaque d'un loup sur un autre en affectant leur point de vie respectif

  Paramètres:
  __________
  ordre_attacque:ordre d'attacquer

  returns
  _______
  dictionnaire : dictionnaire comportant les modification de l'attacque

  version
  _______
  specification: Kenfak tresor  (v.1 19/02/22)
  implementation:Djuideu jason (v.1 21/03/22)

"""
    dictionnaire = dico[0]
    pacifs = dico[1]
    # bonnus dans Attack ************
    werewolves = dictionnaire["WEREWOLVES"]
    joueur1 = werewolves["TEAM_1"]
    joueur2 = werewolves["TEAM_2"]
    bonnus_personne = []
    for pers1 in joueur1:
        k = dictionnaire["WEREWOLVES"]["TEAM_1"][pers1][1]
        for pers2 in joueur1:
            x = pers1[0]
            y = pers1[1]
            w = pers2[0]
            z = pers2[1]
            distance = max(abs(w - x), abs(z - y))
            if dictionnaire["WEREWOLVES"]["TEAM_1"][pers2][0] == "alpha" and distance <= 4 and pers1 != pers2:

                dictionnaire["WEREWOLVES"]["TEAM_1"][pers1][1] = dictionnaire["WEREWOLVES"]["TEAM_1"][pers1][
                                                                     1] + 30

            elif pers1 != pers2 and distance <= 2:

                dictionnaire["WEREWOLVES"]["TEAM_1"][pers1][1] = dictionnaire["WEREWOLVES"]["TEAM_1"][pers1][
                                                                     1] + 10

        bonnus_personne.append([pers1, k, dictionnaire["WEREWOLVES"]["TEAM_1"][pers1][1]])
    for pers1 in joueur2:
        k = dictionnaire["WEREWOLVES"]["TEAM_2"][pers1][1]
        for pers2 in joueur2:
            x = pers1[0]
            y = pers1[1]
            w = pers2[0]
            z = pers2[1]
            distance = max(abs(w - x), abs(z - y))
            if dictionnaire["WEREWOLVES"]["TEAM_2"][pers2][0] == "alpha" and distance <= 4 and pers1 != pers2:
                dictionnaire["WEREWOLVES"]["TEAM_2"][pers1][1] = dictionnaire["WEREWOLVES"]["TEAM_2"][pers1][
                                                                     1] + 30
            elif pers1 != pers2 and distance <= 2:
                dictionnaire["WEREWOLVES"]["TEAM_2"][pers1][1] = dictionnaire["WEREWOLVES"]["TEAM_2"][pers1][
                                                                     1] + 10

        bonnus_personne.append([pers1, k, dictionnaire["WEREWOLVES"]["TEAM_2"][pers1][1]])
        # *************

    if ordre_attacque != []:
        for attack in ordre_attacque:
            attack1 = attack[0]
            attack2 = attack[1]
            x = attack1[0]
            y = attack1[1]
            w = attack2[0]
            z = attack2[1]
            distance = max(abs(w - x), abs(z - y))
            if distance == 1:
                werewolves = dictionnaire["WEREWOLVES"]
                joueur1 = werewolves["TEAM_1"]
                joueur2 = werewolves["TEAM_2"]

                if (attack1 in joueur1 or attack1 in joueur2) and (
                        attack2 in joueur1 or attack2 in joueur2) and (attack1 not in pacifs):
                    if attack1 in joueur1 and attack2 in joueur2 and \
                            dictionnaire["WEREWOLVES"]["TEAM_1"][attack1][1] != 0 and \
                            dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] != 0:

                        dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] = \
                        dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] - \
                        dictionnaire["WEREWOLVES"]["TEAM_1"][attack1][1] * (10 / 100)

                        if dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] < 0:
                            dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] = 0
                    elif attack1 in joueur1 and attack2 in joueur1 and \
                            dictionnaire["WEREWOLVES"]["TEAM_1"][attack1][1] != 0 and \
                            dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] != 0:
                        dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] = \
                        dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] - \
                        dictionnaire["WEREWOLVES"]["TEAM_1"][attack1][1] * (10 / 100)
                        if dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] < 0:
                            dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] = 0

                    elif attack1 in joueur2 and attack2 in joueur1 and \
                            dictionnaire["WEREWOLVES"]["TEAM_2"][attack1][1] != 0 and \
                            dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] != 0:
                        dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] = \
                        dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] - \
                        dictionnaire["WEREWOLVES"]["TEAM_2"][attack1][1] * (10 / 100)

                        if dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] < 0:
                            dictionnaire["WEREWOLVES"]["TEAM_1"][attack2][1] = 0
                    elif attack1 in joueur2 and attack2 in joueur2 and \
                            dictionnaire["WEREWOLVES"]["TEAM_2"][attack1][1] != 0 and \
                            dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] != 0:

                        dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] = \
                        dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] - \
                        dictionnaire["WEREWOLVES"]["TEAM_2"][attack1][1] * (10 / 100)

                        if dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] < 0:
                            dictionnaire["WEREWOLVES"]["TEAM_2"][attack2][1] = 0
            else:
                if attack1 in pacifs:
                    raise ValueError("certain de vos joueur on étè pacifiers")
                else:
                    raise ValueError("a distance entre ces deux points ne sont pas favorable")
            # remise des valeurs
    werewolves = dictionnaire["WEREWOLVES"]
    joueur1 = werewolves["TEAM_1"]
    joueur2 = werewolves["TEAM_2"]
    for position in joueur1:
        for i in range(len(bonnus_personne)):
            if (position == bonnus_personne[i][0]) and not (
                    bonnus_personne[i][2] > dictionnaire["WEREWOLVES"]["TEAM_1"][position][1]):
                dictionnaire["WEREWOLVES"]["TEAM_1"][position][1] = bonnus_personne[i][2] - (
                            bonnus_personne[i][2] - bonnus_personne[i][1])
            elif (position == bonnus_personne[i][0]) and (
                    bonnus_personne[i][2] > dictionnaire["WEREWOLVES"]["TEAM_1"][position][1]):
                dictionnaire["WEREWOLVES"]["TEAM_1"][position][1] = bonnus_personne[i][1] - (
                            bonnus_personne[i][2] - dictionnaire["WEREWOLVES"]["TEAM_1"][position][1])
    for position in joueur2:
        for i in range(len(bonnus_personne)):
            if (position == bonnus_personne[i][0]) and not (
                    bonnus_personne[i][2] > dictionnaire["WEREWOLVES"]["TEAM_2"][position][1]):
                dictionnaire["WEREWOLVES"]["TEAM_2"][position][1] = bonnus_personne[i][2] - (
                            bonnus_personne[i][2] - bonnus_personne[i][1])
            elif (position == bonnus_personne[i][0]) and (
                    bonnus_personne[i][2] > dictionnaire["WEREWOLVES"]["TEAM_2"][position][1]):
                dictionnaire["WEREWOLVES"]["TEAM_2"][position][1] = bonnus_personne[i][1] - (
                            bonnus_personne[i][2] - dictionnaire["WEREWOLVES"]["TEAM_2"][position][1])

    return dictionnaire


def nutrition(ordre_nutrition=ordre_manger, dictionnaire=attack()):
    """ Permet à un loup de récuperer un aliment si la distance lui permet

  Paramètres:
  __________
  ordre_nutrition: ordre qui ordonne a des loups de manger
  dictionnaire:dictionnaire que retourner la fonction attack
  returns
  _______
  dictionnaire: effectuent les modification sur la vie des joueurs qui se sont nourries

  version
  _______
  specification: Djuideu Jason  (v.1 19/02/22)
  implementation:Kenfak tresor (v.1 22/03/22)
  """
    if ordre_nutrition != []:
        for nutri in ordre_nutrition:
            nutrition1 = nutri[0]
            nutrition2 = nutri[1]
            x = nutrition1[0]
            y = nutrition1[1]
            w = nutrition2[0]
            z = nutrition2[1]
            distance = max(abs(w - x), abs(z - y))
            if 1 >= distance >= 0:
                werewolves = dictionnaire["WEREWOLVES"]
                joueur1 = werewolves["TEAM_1"]
                joueur2 = werewolves["TEAM_2"]
                foods = dictionnaire["FOODS"]
                if (nutrition1 in joueur1 or nutrition1 in joueur2) and (nutrition2 in foods):
                    if nutrition1 in joueur1 and 100 >= dictionnaire["WEREWOLVES"]["TEAM_1"][nutrition1][1] >= 0:
                        dictionnaire["WEREWOLVES"]["TEAM_1"][nutrition1][1] = \
                        dictionnaire["WEREWOLVES"]["TEAM_1"][nutrition1][1] + dictionnaire["FOODS"][nutrition2][
                            1]
                        del dictionnaire["FOODS"][nutrition2]
                        if dictionnaire["WEREWOLVES"]["TEAM_1"][nutrition1][1] > 100:
                            dictionnaire["WEREWOLVES"]["TEAM_1"][nutrition1][1] = 100
                    elif nutrition1 in joueur2 and dictionnaire["WEREWOLVES"]["TEAM_2"][nutrition1][
                        1] <= 100 and dictionnaire["WEREWOLVES"]["TEAM_2"][nutrition1][1] >= 0:
                        dictionnaire["WEREWOLVES"]["TEAM_2"][nutrition1][1] = \
                        dictionnaire["WEREWOLVES"]["TEAM_2"][nutrition1][1] + dictionnaire["FOODS"][nutrition2][
                            1]
                        del dictionnaire["FOODS"][nutrition2]
                        if dictionnaire["WEREWOLVES"]["TEAM_2"][nutrition1][1] > 100:
                            dictionnaire["WEREWOLVES"]["TEAM_2"][nutrition1][1] = 100
                else:
                    raise ValueError("se joueur ne peut pas manger")
    return dictionnaire

