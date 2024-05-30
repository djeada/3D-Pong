from src.game import Game


def main():
    game = Game("config.yaml")
    game.initialize()
    game.start()


if __name__ == "__main__":
    main()
