import pygame
import random
import neat
import os
pygame.init()

WIDTH = 600
HEIGHT = 250

gen = 0

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car game")

BG_IMG = pygame.image.load("img/road.png")
CAR_IMG = pygame.image.load("img/car.png")
CAR_OBSTACLE_IMG = pygame.image.load("img/car_obstacle.png")
REPAIR_IMG = pygame.image.load("img/repair.png")

clock = pygame.time.Clock()

# classes
class Road:
    VEL = 3
    IMG_WIDTH = BG_IMG.get_width()
    IMG = BG_IMG

    def __init__(self):
        self.x1 = 0
        self.y1 = 0
        self.x2 = self.IMG_WIDTH
        self.y2 = 0

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.IMG_WIDTH < 0:
            self.x1 = self.x2 + self.IMG_WIDTH

        if self.x2 + self.IMG_WIDTH < 0:
            self.x2 = self.x1 + self.IMG_WIDTH

    def draw(self):
        window.blit(self.IMG, (self.x1, self.y1))
        window.blit(self.IMG, (self.x2, self.y2))

class Car:
    IMG = CAR_IMG

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = self.IMG.get_width()
        self.height = self.IMG.get_height()
        self.vel = 5
        self.health = 10
        self.hitbox = (self.x, self.y, self.width, self.height)

    def draw(self):
        window.blit(self.IMG, (self.x, self.y))
        # hp bar
        # pygame.draw.rect(window, (200, 0, 0), (self.x - 10, self.y, 5, 60))
        # pygame.draw.rect(window, (0, 128, 0), (self.x - 10, self.y, 5, 6 * self.health))
        # hitbox
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vel = 5
        self.health = 10

    def move(self):
        self.y += self.vel


class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = CAR_OBSTACLE_IMG.get_height()
        self.width = CAR_OBSTACLE_IMG.get_width()
        self.vel = 3
        self.hitbox = (self.x, self.y, self.width, self.height)

    def draw(self):
        window.blit(CAR_OBSTACLE_IMG, (self.x, self.y))
        #hitbox
        self.hitbox = (self.x, self.y, self.width, self.height - 5)
        #pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)

    def move(self):
        self.x -= self.vel

# class Orb:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.height = REPAIR_IMG.get_height()
#         self.width = REPAIR_IMG.get_width()
#         self.vel = 3
#         self.hitbox = (self.x, self.y, self.width, self.height)
#
#     def draw(self):
#         window.blit(REPAIR_IMG, (self.x, self.y))
#         #hitbox
#         self.hitbox = (self.x, self.y, self.width, self.height - 5)
#         # pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)
#
#     def move(self):
#         self.x -= self.vel

# global functions
def redraw_game_window(road, cars, obstacles, font, ge):
    gen_text = font.render("Gen: " + str(gen), 1, (255, 255, 255))
    car_alives_text = font.render("Car alives: " + str(len(cars)), 1, (255, 255, 255))

    window.blit(gen_text, (50, 50))
    road.draw()
    for car in cars:
        car.draw()
    for obstacle in obstacles:
        obstacle.draw()
    # for orb in orbs:
    #     orb.draw()
    if len(ge) > 0:
        fitness = ge[0].fitness
    else:
        fitness = 0
    fitness_text = font.render("Fitness: " + str(fitness), 1, (255, 255, 255))
    window.blit(gen_text, (450, 0))
    window.blit(car_alives_text, (450, 30))
    window.blit(fitness_text, (450, 60))
    pygame.display.update()

# main loop
def main(genomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    cars = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        cars.append(Car(15, 50))
        g.fitness = 0
        ge.append(g)

    road = Road()
    obstacles = []
    # orbs = []
    font = pygame.font.SysFont('comicsans', 25, True)
    run = True
    while run:
        clock.tick(200)
        # event to quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if len(cars) <= 0:
            break
        #AI Configuration
        if len(obstacles) >= 1:
            for x, car in enumerate(cars):
                if car.y > 0 - car.vel and car.y <= HEIGHT - car.vel - car.IMG.get_height():
                    car.move()
                for obstacle in obstacles:

                        # output = nets[x].activate((car.y, car.height, obstacle.y, obstacle.height, abs(car.x + car.width - obstacle.x), orb.y,
                        #                            orb.height, orb.x, abs(car.x + car.width - orb.x)))
                    output = nets[x].activate((car.y, car.height, obstacle.y, obstacle.height, abs(car.x + car.width - obstacle.x)))

                    if output[0] > 0.5:
                        car.vel = -5
                    else:
                        car.vel = 5

        for x, car in enumerate(cars):
            for obstacle in obstacles:
                if car.x > obstacle.x + obstacle.width:
                    ge[x].fitness += 1

        # for x, car in enumerate(cars):
        #     for orb in orbs:
        #         if car.x > orb.x + orb.width:
        #             ge[x].fitness -= 1

        # creating obstacle
        if len(obstacles) == 0:
            obstacles.append(Obstacle(500, random.randint(0, HEIGHT - CAR_OBSTACLE_IMG.get_height())))

        # creating orb
        # if len(orbs) == 0:
        #     orbs.append(Orb(500, random.randint(0, HEIGHT - REPAIR_IMG.get_height())))

        # collides with obstacle
        if len(obstacles) >= 1:
            for obstacle in obstacles:
                for x, car in enumerate(cars):
                    if car.hitbox[0] + car.hitbox[2] > obstacle.hitbox[0] and car.hitbox[0] < obstacle.hitbox[0] + obstacle.hitbox[2]:
                        if car.hitbox[1] < obstacle.hitbox[1] + obstacle.hitbox[3] and car.hitbox[1] + car.hitbox[3] > obstacle.hitbox[1]:
                            obstacles.append(Obstacle(500, random.randint(0, HEIGHT - CAR_OBSTACLE_IMG.get_height())))
                            obstacles.pop(0)
                            car.health -= 10
                            ge[x].fitness -= 1

                if obstacle.hitbox[0] + obstacle.hitbox[2] <= 0:
                    obstacles.append(Obstacle(500, random.randint(0, HEIGHT - CAR_OBSTACLE_IMG.get_height())))
                    obstacles.pop(0)

        # collides with orbs
        # if len(orbs) >= 1:
        #     for orb in orbs:
        #         for x, car in enumerate(cars):
        #             if car.hitbox[0] + car.hitbox[2] > orb.hitbox[0] and car.hitbox[0] < orb.hitbox[0] + orb.hitbox[2]:
        #                 if car.hitbox[1] < orb.hitbox[1] + orb.hitbox[3] and car.hitbox[1] + car.hitbox[3] > orb.hitbox[1]:
        #                     orbs.append(Orb(500, random.randint(0, HEIGHT - REPAIR_IMG.get_height())))
        #                     orbs.pop(0)
        #                     ge[x].fitness += 2
        #
        #         if orb.hitbox[0] + orb.hitbox[2] <= 0:
        #             orbs.append(Orb(500, random.randint(0, HEIGHT - REPAIR_IMG.get_height())))
        #             orbs.pop(0)

        # keys
        # for car in cars:
        #     if car.y > 0 - car.vel and car.y <= HEIGHT - car.vel - car.IMG.get_height():
        #         car.move()
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_UP]:
        #     car.vel = -5
        # elif keys[pygame.K_DOWN]:
        #     car.vel = 5

        #ending game
        for x, car in enumerate(cars):
            if car.health <= 0:
                cars.pop(x)
                nets.pop(x)
                ge.pop(x)

        # last settings
        for obstacle in obstacles:
            obstacle.move()
        # for orb in orbs:
        #     orb.move()
        road.move()

        redraw_game_window(road, cars, obstacles, font, ge)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)