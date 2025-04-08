import pygame as py
import random
import os
import neat
import pickle
from projekt.player import Player
from projekt.platformdk import PlatformDK
from projekt.border import Border
from projekt.ladder import Ladder
from projekt.barrel import Barrel
from projekt.ladder_detect import LadderDetect
from projekt.princess import Princess
from projekt.config import *
from visualizeNEAT import VisualizeNN

MIN_BARREL_SPAWN = 1000
MAX_BARREL_SPAWN = 5000

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.clock = py.time.Clock()

        self.borders = [Border(x, y, width, height) for (x, y, width, height) in Border.border_positions]
        self.platforms = [PlatformDK(x, y, width, height) for (x, y, width, height) in PlatformDK.platform_positions]
        self.ladders = [Ladder(x, y, width, height) for (x, y, width, height) in Ladder.ladder_positions]
        #self.ladders_detect = [LadderDetect(x, y, width, height) for (x, y, width, height) in LadderDetect.ladder_detect_positions]

        self.barrels = []
        self.player = Player(PLAYER_X, PLAYER_Y, self.platforms, self.borders, self.ladders)
        self.princess = Princess(PRINCESS_X, PRINCESS_Y, self.player)
        self.level_image = py.image.load(os.path.join('Assets', 'level.png')).convert()

        self.NEW_BARREL_EVENT = py.USEREVENT + 1
        py.time.set_timer(self.NEW_BARREL_EVENT, random.randint(MIN_BARREL_SPAWN, MAX_BARREL_SPAWN))
        self.game_over = False
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.txt')

        self.barrel_remover = py.Rect(10, 710, 50, 50)
        self.neat_visualizer = VisualizeNN(pos=(self.screen_width - 600, self.screen_height - 600),
                                           size=(600, 600), update_interval=30)

        self.max_lifetime = 10

    def draw_eval(self, players, neat_img=None, overlay_data=None):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.level_image, (0, 0))

        for platform in self.platforms:
            self.screen.blit(platform.image, platform.rect)
        for border in self.borders:
            self.screen.blit(border.image, border.rect)
        for ladder in self.ladders:
            self.screen.blit(ladder.image, ladder.rect)
        '''for ladder_detect in self.ladders_detect:
            self.screen.blit(ladder_detect.image, ladder_detect.rect)'''
        for barrel in self.barrels:
            barrel.draw(self.screen)
        self.princess.draw(self.screen)

        for player in players:
            player.draw(self.screen)

        '''    for player in players:
            for platform in self.platforms:
                self.screen.blit(platform.image, platform.rect)
            for border in self.borders:
                self.screen.blit(border.image, border.rect)
            for ladder in self.ladders:
                self.screen.blit(ladder.image, ladder.rect)
            for ladder_detect in self.ladders_detect:
                self.screen.blit(ladder_detect.image, ladder_detect.rect)
            for barrel in self.barrels:
                barrel.draw(self.screen)
            self.princess.draw(self.screen)
            player.draw(self.screen)'''

        if neat_img is not None:
            self.screen.blit(neat_img, (self.screen_width - 600, self.screen_height - 600))
        if overlay_data is not None:
            font = py.font.SysFont("comicsans", 20)
            x_offset = self.screen_width - 300
            y_offset = 10
            lines = [
                f"Gen: {overlay_data['generation']}",
                f"Alive: {overlay_data['alive']}",
                f"Max Fit: {overlay_data['max_fitness']:.2f}"
            ]
            for line in lines:
                text_surface = font.render(line, True, WHITE)
                self.screen.blit(text_surface, (x_offset, y_offset))
                y_offset += text_surface.get_height() + 5
        py.display.flip()

    def draw(self, neat_img=None, overlay_data=None):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.level_image, (0, 0))
        for platform in self.platforms:
            self.screen.blit(platform.image, platform.rect)
        for border in self.borders:
            self.screen.blit(border.image, border.rect)
        for ladder in self.ladders:
            self.screen.blit(ladder.image, ladder.rect)
        '''for ladder_detect in self.ladders_detect:
            self.screen.blit(ladder_detect.image, ladder_detect.rect)'''
        for barrel in self.barrels:
            barrel.draw(self.screen)

        self.princess.draw(self.screen)

        if self.player is not None:
            self.player.draw(self.screen)
        if neat_img is not None:
            self.screen.blit(neat_img, (self.screen_width - 600, self.screen_height - 600))
        py.display.flip()

    def update(self):
        keys = py.key.get_pressed()
        if self.player is not None:
            self.player.update_player(keys, self.platforms)
            if self.player.rect.colliderect(self.princess.rect):
                self.player = None
        for barrel in self.barrels:
            barrel.update_barrel()
            if self.player and self.player.rect.colliderect(barrel.rect):
                print("Game over.")
                self.game_over = True

        for barrel in self.barrels[:]:
            if barrel.rect.colliderect(self.barrel_remover):
                self.barrels.remove(barrel)


    def run_neat(self, config_path, generations=50, simulation_frames=3000):
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)
        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        p.add_reporter(neat.StatisticsReporter())

        gen = 0

        def eval_genomes(genomes, config):
            nonlocal gen
            gen += 1

            # svakih 5 generacija im dam 5 sekundi zivota vise
            if gen % 5 == 0:
                self.max_lifetime += 5
                print(f"Nova max_lifetime vrijednost: {self.max_lifetime} sekundi")

            max_frames = self.max_lifetime * FPS  # najveci broj frameova prije nego sto ih obrisem

            self.barrels = []
            nets = []
            players = []
            ge = []

            for genome_id, genome in genomes:
                genome.fitness = 0
                net = neat.nn.FeedForwardNetwork.create(genome, config)
                nets.append(net)
                p_inst = Player(PLAYER_X, PLAYER_Y, self.platforms, self.borders, self.ladders)
                p_inst.best_y = p_inst.rect.y
                players.append(p_inst)
                ge.append(genome)

            frame = 0
            neat_viz_surface = None

            while frame < max_frames and players:  # brisem ih ako prestignu max frames
                for event in py.event.get():
                    if event.type == py.QUIT:
                        py.quit()
                        exit()
                    elif event.type == self.NEW_BARREL_EVENT:
                        new_barrel = Barrel(BARREL_X, BARREL_Y, self.platforms, self.borders)
                        self.barrels.append(new_barrel)
                        new_interval = random.randint(MIN_BARREL_SPAWN, MAX_BARREL_SPAWN)
                        py.time.set_timer(self.NEW_BARREL_EVENT, new_interval)

                for barrel in self.barrels:
                    barrel.update_barrel()

                # brisanje barrela kad izadje iz ekrana
                for barrel in self.barrels[:]:
                    if (barrel.rect.right < 0 or barrel.rect.left > SCREEN_WIDTH or
                            barrel.rect.top > SCREEN_HEIGHT or barrel.rect.bottom < 0):
                        self.barrels.remove(barrel)

                for i in range(len(players) - 1, -1, -1):
                    player = players[i]
                    self.player = players[i]
                    self.platforms = players[i].platforms

                    # nagrada za preskakanje barrela
                    for barrel in self.barrels:
                        if (barrel.rect.right > player.rect.left and barrel.rect.left < player.rect.right and
                                barrel.rect.top > player.rect.bottom and 0 < (
                                        barrel.rect.top - player.rect.bottom) < 20):
                            ge[i].fitness += 5  # nagrada za izbjegavanje

                    # ako ga barrel pogodi brisem ga
                    hit_by_barrel = any(player.rect.colliderect(barrel.rect) for barrel in self.barrels)
                    if hit_by_barrel:
                        ge[i].fitness -= 20  # kazna za sudar
                        del players[i]
                        del nets[i]
                        del ge[i]
                        continue

                    # ako propadne kroz border brisem ga
                    if (player.rect.x < 0 or player.rect.x > SCREEN_WIDTH or
                            player.rect.y < 0 or player.rect.y > SCREEN_HEIGHT):
                        del players[i]
                        del nets[i]
                        del ge[i]
                        continue

                    # bonus fitness za novodosegnutu visinu
                    if player.rect.y < player.best_y:
                        bonus = player.best_y - player.rect.y
                        ge[i].fitness += bonus
                        player.best_y = player.rect.y

                    # aktiviranje nn
                    inputs = player.get_network_inputs(self.ladders, self.barrels)
                    output = nets[i].activate(inputs)

                    #print(output)

                    print(f"Igrač {i} | Ulazi: {['{:.2f}'.format(v) for v in inputs]} | Izlazi: {['{:.2f}'.format(o) for o in output]}")
                    actions = []
                    if output[0] > 0.8:
                        actions.append("SKOK")
                    if output[1] > 0.6:
                        actions.append("DESNO")
                    elif output[1] < 0.4:
                        actions.append("LIJEVO")
                    #if output[2] > 0.6:
                    #    actions.append("GORE")
                    #elif output[2] < 0.4:
                    #    actions.append("DOLJE")

                    print(f"Igrač {i} | Akcije: {', '.join(actions) if actions else 'STOJI'}")

                    prev_y, prev_x = player.y, player.x

                    # nn pokrece igraca
                    if output[0] > 0.5:
                        player.upup()
                    if output[1] > 0.5:
                        player.move_left()
                    elif output[1] < 0.5:
                        player.move_right()
                    #if output[2] > 0.5:
                    #    player.move_up()
                    #elif output[2] < 0.5:
                    #    player.move_down()

                    # primjena gravitacije
                    player.vel_y += player.gravity
                    player.y += player.vel_y
                    player.rect.y = player.y

                    # kolizije
                    player.check_collision_platform(self.platforms, prev_y, prev_x)
                    player.check_collision_border(self.borders, prev_x)

                    # kada dotakne princezu gotovo je
                    if player.rect.colliderect(self.princess.rect):
                        print(f"Igrač {i} je dosegao princezu! Kraj evaluacije.")
                        ge[i].fitness += 1000  # fitness bonus jer je dobar
                        self.save_winner(ge[i])
                        return

                if players and ge:
                    best_genome = max(ge, key=lambda g: g.fitness)
                    self.neat_visualizer.update_visual(config, best_genome)
                    neat_viz_surface = self.neat_visualizer.image

                overlay_data = {
                    "generation": gen,
                    "alive": len(players),
                    "max_fitness": max([g.fitness for g in ge]) if ge else 0
                }
                self.draw_eval(players, neat_img=neat_viz_surface, overlay_data=overlay_data)

                self.clock.tick(FPS)
                frame += 1

            print("Isteklo vrijeme! Svi preostali igrači su obrisani.")
            players.clear()
            nets.clear()
            ge.clear()

        winner = p.run(eval_genomes, generations)
        print('\nBest genome:\n{!s}'.format(winner))

    '''def run(self):
        while True:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    exit()
                elif event.type == self.NEW_BARREL_EVENT:
                    new_barrel = Barrel(BARREL_X, BARREL_Y, self.platforms, self.borders)
                    self.barrels.append(new_barrel)
                    new_interval = random.randint(MIN_BARREL_SPAWN, MAX_BARREL_SPAWN)
                    py.time.set_timer(self.NEW_BARREL_EVENT, new_interval)
        
            self.update()
            self.draw()
            self.clock.tick(FPS)'''

    def run(self):
        while not self.game_over:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    exit()
                elif event.type == self.NEW_BARREL_EVENT:
                    new_barrel = Barrel(BARREL_X, BARREL_Y, self.platforms, self.borders)
                    self.barrels.append(new_barrel)
                    new_interval = random.randint(MIN_BARREL_SPAWN, MAX_BARREL_SPAWN)
                    py.time.set_timer(self.NEW_BARREL_EVENT, new_interval)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        # igra je gotova
        print("Game over. Press R to restart.")
        while True:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    exit()
                elif event.type == py.KEYDOWN:
                    if event.key == py.K_r:
                        print("Game restart...")
                        self.__init__(self.screen)
                        self.run()
                        return
                    elif event.key == py.K_ESCAPE:
                        py.quit()
                        exit()

    def save_winner(self, genome):
        with open("winner.pkl", "wb") as f:
            pickle.dump(genome, f)
        print("Pobjednik je spremljen u 'winner.pkl'!")

    def load_winner(self):
        try:
            with open("winner.pkl", "rb") as f:
                genome = pickle.load(f)
            print("Učitan pobjednički genome!")
            return genome
        except FileNotFoundError:
            print("Nema spremljenog pobjednika!")
            return None

    def run_winner(self, config_path):
        genome = self.load_winner()
        if genome is None:
            print("Nema spremljenog pobjednika! Pokretanje nije moguće.")
            return

        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        player = Player(PLAYER_X, PLAYER_Y, self.platforms, self.borders, self.ladders)

        frame = 0
        while True:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    exit()

            inputs = player.get_network_inputs(self.ladders, self.barrels)
            output = net.activate(inputs)

            if output[0] > 0.8:
                player.upup()
            if output[1] > 0.5:
                player.move_right()
            elif output[1] < 0.5:
                player.move_left()
            '''if output[2] > 0.5:
                player.move_up()
            elif output[2] < 0.5:
                player.move_down()'''

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.level_image, (0, 0))
            for platform in self.platforms:
                self.screen.blit(platform.image, platform.rect)
            player.draw(self.screen)
            py.display.flip()

            self.clock.tick(FPS)
            frame += 1

