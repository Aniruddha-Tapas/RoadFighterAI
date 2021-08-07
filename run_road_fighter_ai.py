"""
The classic game of road fighter
"""
import neat
import pygame
import random
import os
import numpy as np
import pickle
import visualize

pygame.font.init()  # init font

WIN_WIDTH = 400
WIN_HEIGHT = 800

ROAD_LEFT_BOUNDARY = 100
ROAD_RIGHT_BOUNDARY = 340

FRAME_VEL = 15

STAT_FONT = pygame.font.SysFont("lucidacalligraphy", 18)
SCORE_FONT = pygame.font.SysFont("lucidacalligraphy", 18)

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Road Fighter")

carsize = (33, 44)
red = pygame.transform.scale(pygame.image.load(os.path.join("images", "redcar.png")).convert_alpha(), carsize)
yellow = pygame.transform.scale(pygame.image.load(os.path.join("images", "yellowcar.png")).convert_alpha(), carsize)
otherred = pygame.transform.scale(pygame.image.load(os.path.join("images", "otherredcar.png")).convert_alpha(), carsize)
blue = pygame.transform.scale(pygame.image.load(os.path.join("images", "bluecar.png")).convert_alpha(), carsize)
regen = pygame.image.load(os.path.join("images", "regencar.png")).convert_alpha()
truck = pygame.image.load(os.path.join("images", "truck.png")).convert_alpha()
base_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "base.png")).convert_alpha(), (400, 800))
crash = pygame.transform.scale(pygame.image.load(os.path.join("images", "crash_1.png")), (60, 60))

gen = 0
best_score = 0

class RedCar:
    def __init__(self, x, y):
        """
        Initialize the protagonist Red Car object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tick_count = 0
        self.vel = 5
        self.img = red
        self.width = self.img.get_width()

    def turn(self, dir):
        if dir == 'left':
            self.x = self.x - self.vel
        if dir == 'right':
            self.x = self.x + self.vel

    def move(self):
        """
        make the car move
        :return: None
        """
        self.tick_count += 1

    def draw(self, win):
        """
        draw the car
        :param win: pygame window or surface
        :return: None
        """
        win.blit(self.img, (self.x, self.y))


class OtherCar:

    def __init__(self, color, id, y, dir=None):
        """
        Initialize the antagonist Other Car object
        :param color: Str, one of [yellow, blue, otherred]
        :param y: starting y pos (int)
        :param dir: Str, one of the directions [left, right]
        :return: None
        """
        self.color = color
        if color == "yellow":
            self.img = yellow
        elif color == "blue":
            self.img = blue
        else:
            self.img = otherred
        self.width = self.img.get_width()
        self.id = id
        self.x = random.randrange(ROAD_LEFT_BOUNDARY, ROAD_RIGHT_BOUNDARY - self.width)
        self.y = y
        self.origin = (self.x, self.y)
        self.dir = dir
        self.vel = FRAME_VEL
        self.passed = False
        self.shift = True
        self.reverse = False
        self.distance = 0

    def move(self):
        """
        make the car move
        :return: None
        """
        self.y += self.vel

    def turn(self):
        """
        makes the car turn left or right
        :return: None
        """
        if self.dir == "right":
            if self.x + 4 < min(ROAD_RIGHT_BOUNDARY - self.width, self.origin[0] + 64):
                self.x += 4

        if self.dir == "left":
            if self.x - 4 > max(ROAD_LEFT_BOUNDARY, self.origin[0] - 64):
                self.x -= 4

    def turn_and_reverse(self):
        """
        make the car turn left or right and then back to it's original position
        :return: None
        """
        if self.dir == "right":
            right_bound = [ROAD_RIGHT_BOUNDARY - self.width, self.origin[0] + 64]
            argmin = np.argmin(right_bound)
            if self.shift and self.x + 4 < min(right_bound):
                self.x += 4
                self.distance += 4

            if (argmin == 1 and self.distance >= 60) or (argmin == 0 and self.x >= right_bound[0] - 4):
                self.shift = False
                self.reverse = True

            if self.reverse:
                if self.distance > 0:
                    self.x = self.x - 4
                    self.distance -= 4
                else:
                    self.reverse = False
                    self.distance = 0

        if self.dir == "left":
            left_bound = [ROAD_LEFT_BOUNDARY, self.origin[0] - 64]
            argmax = np.argmax(left_bound)
            if self.shift and self.x - 4 > max(left_bound):
                self.x -= 4
                self.distance += 4

            if (argmax == 1 and self.distance >= 60) or (argmax == 0 and self.x <= left_bound[0] + 4):
                self.shift = False
                self.reverse = True

            if self.reverse:
                if self.distance > 0:
                    self.x = self.x + 4
                    self.distance -= 4
                else:
                    self.reverse = False
                    self.distance = 0

    def draw(self, win):
        """
        draw the car
        :param win: pygame window or surface
        :return: None
        """
        win.blit(self.img, (self.x, self.y))

    def collide(self, car, win):
        """
        returns if the red car rectangle is colliding with another car rectangle
        :param RedCar: The red car object
        :return: Bool
        """
        car_width = round(2 * carsize[0] / 3 + 2)
        currentcar_width = round(2 * carsize[0] / 3)
        if self.x > car.x + car_width or car.x > self.x + currentcar_width:
            return False
        if self.y + round(carsize[1] / 2) < car.y or self.y > car.y + round(carsize[1] / 2):
            return False
        return True

    def __repr__(self):
        return "{} Car {} {}".format(self.color, self.id, self.origin)


class Base:
    """
    Represents the moving road of the game
    """
    WIDTH = base_img.get_width()
    HEIGHT = base_img.get_height()
    IMG = base_img

    def __init__(self):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.x = 0
        self.y1 = 0
        self.vel = FRAME_VEL
        self.y2 = self.HEIGHT

    def move(self):
        """
        move road so it looks like its scrolling
        :return: None
        """
        self.y1 += self.vel
        self.y2 += self.vel

        if self.y1 > self.HEIGHT:
            self.y1 = self.y2 - self.HEIGHT

        if self.y2 > self.HEIGHT:
            self.y2 = self.y1 - self.HEIGHT

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x, self.y1))
        win.blit(self.IMG, (self.x, self.y2))


def end_screen(win):
    """
    display an end screen when the player loses
    :param win: the pygame window surface
    :return: None
    """
    run = True
    text_label = STAT_FONT.render("Press Space to Restart", 1, (0, 0, 0))
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                main(win, True)

        win.blit(text_label, ((ROAD_LEFT_BOUNDARY + ROAD_RIGHT_BOUNDARY)/ 2 - text_label.get_width() / 2, WIN_HEIGHT/2))
        pygame.display.update()

    pygame.quit()
    quit()


def get_mask(img):
    """
    gets the mask for the current image
    :return: None
    """
    return pygame.mask.from_surface(img)


def draw_window(win, redcars, othercars, base, score):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param redcars: a List of Red Car objects
    :param othercars: List of other cars
    :param score: score of the game (int)
    :return: None
    """
    win.blit(base_img, (0, 0))
    base.draw(win)
    for car in othercars:
        car.draw(win)
    for redcar in redcars:
        redcar.draw(win)
    score_label = SCORE_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score_label, (2, 20))
    pygame.display.update()


def main(genomes, config):
    """
    Runs the simulation of the current population of
    red cars and sets their fitness based on the number of other cars
    they reach in the game.
    """
    global WIN, gen, best_score
    win = WIN

    nets = []
    ge = []
    reds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        reds.append(RedCar(250, 750))
        g.fitness = 0
        ge.append(g)

    base = Base()

    random_car = OtherCar("yellow", 4, random.randint(-700, -600))
    random_car_int = random.randint(0, 2)
    if random_car_int == 1:
        random_car = OtherCar("blue", 4, random.randint(-700, -600), dir=random.choice(['left', 'right']))
    elif random_car_int == 2:
        random_car = OtherCar("otherred", 4, random.randint(-700, -600), dir=random.choice(['left', 'right']))

    othercars = [OtherCar("yellow", 1, 0),
                 OtherCar("yellow", 2, random.randint(-350, -200)),
                 OtherCar("yellow", 3, random.randint(-550, -400)),
                 random_car]

    score = 0
    clock = pygame.time.Clock()

    move_left = False
    move_right = False

    run = True

    while run:

        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            #         move_left = True
            #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            #         move_right = True
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            #         move_left = False
            #     elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            #         move_right = False


        base.move()


        # determine which car to use for neural network input
        car_ind = 0
        if len(reds) > 0:
            if len(othercars) > 1 and reds[0].y < othercars[0].y:
                car_ind = 1
            elif len(othercars) > 2 and reds[0].y < othercars[1].y:
                car_ind = 2
            elif len(othercars) > 3 and reds[0].y < othercars[2].y:
                car_ind = 3
        else:
            run = False
            break

        # give each red car a fitness of 0.1 for each frame it stays alive
        for x, red in enumerate(reds):
            ge[x].fitness += 0.1

            # send red location, other car location and determine from network
            # where to turn if at all
            output = nets[x].activate((red.x,
                                       othercars[car_ind].x + round((2 * carsize[0] / 3)/2),
                                       othercars[car_ind].y + round(carsize[1] / 2)))

            # we use a tanh activation function so result will be between -1 and 1.
            if output[0] > 0.5:
                red.turn("right")
            if output[0] < -0.5:
                red.turn("left")

        # if move_left:
        #     red.turn("left")
        # if move_right:
        #

        rem = []
        add_car = False
        passed_car_id = 0

        for car in othercars:
            car.move()

            if car.color == "blue" and car.y > random.randint(400, 500):
                car.turn()

            if car.color == "otherred" and car.y > random.randint(350, 450):
                car.turn_and_reverse()

            for x, redx in enumerate(reds):

                if car.collide(redx, win):
                    ge[x].fitness -= 1
                    nets.pop(x)
                    ge.pop(x)
                    reds.pop(x)

                if not car.passed and redx.y < car.y:
                    car.passed = True
                    add_car = True
                    passed_car_id = car.id
                    passed_car_id += 1
                    passed_car_id = passed_car_id % 4

            if car.y > WIN_HEIGHT:
                rem.append(car)

        if add_car:
            score += 1
            for g in ge:
                g.fitness += 5

            added_car_y = 0
            car_to_be_added = OtherCar("yellow", passed_car_id, added_car_y)
            if passed_car_id == 4 or passed_car_id == 0:
                random_car_int = random.randint(0, 1)
                if random_car_int == 1:
                    car_to_be_added = OtherCar("blue", 4, added_car_y,
                                               dir=random.choice(['left', 'right']))
                else:
                    car_to_be_added = OtherCar("otherred", 4, added_car_y,
                                               dir=random.choice(['left', 'right']))
            othercars.append(car_to_be_added)

        for r in rem:
            othercars.remove(r)

        for redz in reds:
            if redz.x < ROAD_LEFT_BOUNDARY or redz.x + redz.width > ROAD_RIGHT_BOUNDARY:
                nets.pop(reds.index(redz))
                ge.pop(reds.index(redz))
                reds.pop(reds.index(redz))

        draw_window(win, reds, othercars, base, score)

        if score > best_score:
            best_score = score
            print("Woohooo!!! Best Score! :D", score)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play road fighter.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)


    # Unpickle saved winner
    with open("winner-road-fighter.pkl", "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    main(genomes, config)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
