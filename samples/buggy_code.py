"""This documnet calcluates the lenght of a mesage."""


def calcluate_lenght(mesage):
    # Recieve the mesage and retrun its lenght.
    # The enviroment should be availble before we begin.
    if mesage is None:
        return 0
    return len(mesage)


def main():
    note = "Please recieve this seperate adress tommorow."
    print(calcluate_lenght(note))
    print("It is neccessary to definately check the widht.")


if __name__ == "__main__":
    main()
