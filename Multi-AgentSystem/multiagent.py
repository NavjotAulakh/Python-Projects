#!/usr/bin/env python
from __future__ import division
import pygame
import sys
import time
import random
import queue
import numpy as np
from scipy.spatial import distance
from pygame.locals import *
import csv

FPS = 1000
pygame.init()
fpsClock = pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 100, 100
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Multi-Agent System")
fake_screen = screen.copy()
surface = pygame.Surface((100, 100))
surface.fill((0, 0, 0))
clock = pygame.time.Clock()

GRIDSIZE = 1
GRID_WIDTH = 100
GRID_HEIGHT = 100
scen1_iter = 0
scen2_iter = 0
scen3_iter = 0
total_iter = 0
scen1i = 0
scen1k = 0
scen2i = 0
scen2k = 0
scen3i = 0
scen3k = 0
np.set_printoptions(precision=64)
with open('g4_1.csv', 'w') as csvfile:
    fieldnames = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

with open('g4_2.csv', 'w') as csvfile:
    fieldnames = ['Scen #', 'Avg i', 'Avg k']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)


def game(scen, iter):
    allnodes = []
    for x in xrange(0, 99, 1):
        for y in xrange(0, 99, 1):
                allnodes.append([x, y])

    dirs = [[1, 0], [0, 1], [-1, 0], [0,-1]]
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    COLORS = [(255, 255, 0),
              (0, 255, 0),
              (255, 0, 0),
              (0, 0, 255),
              (255, 255, 255)]
    pagentT = np.array([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], np.int32)
    pagent1T = np.array([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], np.int32)
    pagent2T = np.array([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], np.int32)
    pagent3T = np.array([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], np.int32)
    pagent4T = np.array([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], np.int32)
    array = np.array([[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), \
        (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]], np.int32)
    fringe = np.array([[(0, 0), (0, 0), (0, 0), (0, 0)]], np.int32)

    def agentproperties():
        fpsClock = pygame.time.Clock()

    def draw_map(surf, color, pos):
        r = pygame.Rect((pos[0], pos[1]), (GRIDSIZE, GRIDSIZE))
        pygame.draw.rect(surf, color, r)

    def draw_agent(surf, color, pos):
        r = pygame.Rect((pos[0], pos[1]), (GRIDSIZE, GRIDSIZE))
        pygame.draw.rect(surf, color, r)

    def draw_target(surf, color, pos):
        r = pygame.Rect((pos[0], pos[1]), (GRIDSIZE, GRIDSIZE))
        pygame.draw.rect(surf, color, r)

    class Agent(object):
        def __init__(self):
            self.update()
            self.color = random.choice(COLORS)
            COLORS.remove(self.color)
            self.frontier = queue.Queue()
            self.prevpath = []
            self.collected = np.array([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], np.int32)
            self.check = bool(1)
            self.samedir = 0
            self.state = 0
            self.rt = 0
            self.reacht = (0, 0)
            self.goal = 0
            self.gtrust = 60
            self.otrust = np.array([60, 60, 60, 60, 60], np.int32)

        def get_head_position(self):
            return self.positions[0]

        def update(self):
            self.steps = 0
            self.positions = [(random.randint(0, GRID_WIDTH - 1) * GRIDSIZE, random.randint(0, GRID_HEIGHT - 1) * GRIDSIZE)]
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        def point(self, pt):
                self.direction = pt

        def realmove(self):
            cur = self.positions[0]
            count = 0
            wait = 0
            if len(self.prevpath) > 500:
                self.prevpath = []
            while self.check:
                x, y = self.direction
                new = (cur[0] + x, cur[1] + y)
                if (new in self.prevpath) & (count < 5):
                    self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                    if (cur[1] + y) > 95:
                        self.direction = (0, -1)
                    elif (cur[1] + y) < 5:
                        self.direction = (0, 1)
                    elif (cur[0] + x) > 95:
                        self.direction = (-1, 0)
                    elif (cur[0] + x) < 5:
                        self.direction = (1, 0)
                    count += 1
                else:
                    self.check = bool(0)
            self.check = bool(1)

        def reach(self):
            self.steps = self.steps + 1
            cur = self.positions[0]
            x, y = self.direction
            coun=0
            for a in range(5):
                if self.positions[0] != agents[a].positions[0]:
                        while (abs(distance.euclidean((cur[0] + x, cur[1] + y), agents[a].positions[0])) < 10) & (
                                coun < 20) & (abs(distance.euclidean((cur[0] + x, cur[1] + y), agents[a].positions[0])) <= (
                                abs(distance.euclidean((cur[0], cur[1]), agents[a].positions[0])))):
                            x, y = self.direction
                            self.direction = random.choice([(x, -y), (-x, y), (-x, -y)])
                            coun += 1
            while abs(distance.euclidean((cur[0] + x, cur[1] + y), self.reacht)) >= abs(distance.euclidean((cur[0], cur[1]), self.reacht)):
                x, y = self.direction
                self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                if abs(distance.euclidean((cur[0], cur[1]), self.reacht) - distance.euclidean((cur[0] + x, cur[1] + y), self.reacht)) <= 10:
                    self.state = 0
                    break
            x, y = self.direction
            new = (cur[0] + x, cur[1] + y)
            if len(self.positions) > 2 and new in self.positions[2:]:
                self.update()
            else:
                self.positions.insert(0, new)
                if len(self.positions) > 1:
                    self.positions.pop()

        def move(self):
            self.steps = self.steps + 1
            cur = self.positions[0]
            self.frontier.put(cur)
            if cur not in self.prevpath:
                self.prevpath.append(cur)
            x, y = self.direction
            if (cur[1] + y) > 95:
                self.direction = (0, -1)
            elif (cur[1] + y) < 5:
                self.direction = (0, 1)
            elif (cur[0] + x) > 95:
                self.direction = (-1, 0)
            elif (cur[0] + x) < 5:
                self.direction = (1, 0)
            x, y = self.direction
            new = (cur[0] + x, cur[1] + y)
            self.realmove()
            if (x, y) == self.direction:
                self.samedir += 1
            if self.samedir > 20:
                self.direction = random.choice([(x, -y), (-x, y), (-x, -y)])
                self.samedir = 0
            counm = 0
            for a in range(5):
                if self.positions[0] != agents[a].positions[0]:
                    while (abs(distance.euclidean((cur[0] + x, cur[1] + y), agents[a].positions[0])) < 10) & (
                            counm < 20) & (
                            abs(distance.euclidean((cur[0] + x, cur[1] + y), agents[a].positions[0])) <= (
                            abs(distance.euclidean((cur[0], cur[1]), agents[a].positions[0])))):
                        x, y = self.direction
                        self.direction = random.choice([(x, -y), (-x, y), (-x, -y)])
                        counm += 1
            if len(self.positions) > 2 and new in self.positions[2:]:
                self.update()
            else:
                self.positions.insert(0, new)
                if len(self.positions) > 1:
                    self.positions.pop()

        def draw(self, surf):
            for p in self.positions:
                draw_agent(surf, self.color, p)
                draw_map(surf, self.color, p)
                draw_target(surf, self.color, p)

    class Target(object):
        def __init__(self):
            self.position = (0, 0)
            self.color = agent.color
            self.randomize()

        def randomize(self):
            self.position = (random.randint(0, GRID_WIDTH - 1) * GRIDSIZE, random.randint(0, GRID_HEIGHT - 1) * GRIDSIZE)

        def draw(self, surf):
            draw_target(surf, self.color, self.position)

        def collected(self):
            self.color = (0, 0, 0)
            self.position = (-1000, -1000)
    if scen == 0:
        pygame.display.set_caption("Multi-Agent System - Scenerio 1 | Iteration # " + str(iter+1))
    elif scen == 1:
        pygame.display.set_caption("Multi-Agent System - Scenerio 2 | Iteration # " + str(iter+1))
    else:
        pygame.display.set_caption("Multi-Agent System - Scenerio 3 | Iteration # " + str(iter+1))
    agent = Agent()
    targetA1 = Target()
    targetA2 = Target()
    targetA3 = Target()
    targetA4 = Target()
    targetA5 = Target()
    agent1 = Agent()
    targetB1 = Target()
    targetB1.color = agent1.color
    targetB2 = Target()
    targetB2.color = agent1.color
    targetB3 = Target()
    targetB3.color = agent1.color
    targetB4 = Target()
    targetB4.color = agent1.color
    targetB5 = Target()
    targetB5.color = agent1.color
    agent2 = Agent()
    targetC1 = Target()
    targetC1.color = agent2.color
    targetC2 = Target()
    targetC2.color = agent2.color
    targetC3 = Target()
    targetC3.color = agent2.color
    targetC4 = Target()
    targetC4.color = agent2.color
    targetC5 = Target()
    targetC5.color = agent2.color
    agent3 = Agent()
    targetD1 = Target()
    targetD1.color = agent3.color
    targetD2 = Target()
    targetD2.color = agent3.color
    targetD3 = Target()
    targetD3.color = agent3.color
    targetD4 = Target()
    targetD4.color = agent3.color
    targetD5 = Target()
    targetD5.color = agent3.color
    agent4 = Agent()
    targetE1 = Target()
    targetE1.color = agent4.color
    targetE2 = Target()
    targetE2.color = agent4.color
    targetE3 = Target()
    targetE3.color = agent4.color
    targetE4 = Target()
    targetE4.color = agent4.color
    targetE5 = Target()
    targetE5.color = agent4.color
    agents = [agent, agent1, agent2, agent3, agent4]
    atargets = [targetA1, targetA2, targetA3, targetA4, targetA5]
    btargets = [targetB1, targetB2, targetB3, targetB4, targetB5]
    ctargets = [targetC1, targetC2, targetC3, targetC4, targetC5]
    dtargets = [targetD1, targetD2, targetD3, targetD4, targetD5]
    etargets = [targetE1, targetE2, targetE3, targetE4, targetE5]

    def check_target(agent, target):
        temp = 0
        temp1 = 0
        temp2 = 0
        temp3 = 0
        temp4 = 0
        for a in range(len(agents)):
            for t in range(len(atargets)):
                if distance.euclidean(agents[0].get_head_position(), atargets[t].position) < 10:
                    agents[0].collected[t] = atargets[t].position
                    atargets[t].collected()
                    array[0][t] = atargets[t].position
                    atargets[t].position = (-1000, -1000)
                    agents[0].goal += 1
                if (distance.euclidean(agents[a].get_head_position(), atargets[t].position) < 10) \
                        & np.any(array[0][t] != (-1000, -1000)):
                    if scen == 0:
                        decision = random.randint(0, (7-agents[a].goal))
                        if decision < 3:
                            array[0][t] = atargets[t].position
                            pagentT[t] = atargets[t].position
                        else:
                            array[0][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagentT[t] = (random.randint(10, 90), random.randint(10, 90))
                    elif scen == 1:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 4:
                            if agents[a].otrust[0] > 60:
                                array[0][t] = atargets[t].position
                                pagentT[t] = atargets[t].position
                                if np.any(temp != pagentT[t]):
                                    agents[0].otrust[a] += 1
                                temp = array[0][t]
                        else:
                            array[0][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagentT[t] = (random.randint(10, 90), random.randint(10, 90))
                            if np.any(temp != pagentT[t]):
                                agents[0].otrust[a] -= 1
                            temp = array[0][t]
                    else:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 5 & (abs(agents[4].goal - agents[a].goal) > 2):
                            if agents[a].otrust[0] > 60:
                                array[0][t] = atargets[t].position
                                pagentT[t] = atargets[t].position
                                if np.any(temp != pagentT[t]):
                                    agents[0].otrust[a] += 1
                                temp = array[0][t]

                if distance.euclidean(agents[1].get_head_position(), btargets[t].position) < 10:
                    agents[1].collected[t] = btargets[t].position
                    btargets[t].collected()
                    array[1][t] = btargets[t].position
                    btargets[t].position = (-1000, -1000)
                    agents[1].goal += 1
                if (distance.euclidean(agents[a].get_head_position(), btargets[t].position) < 10) \
                        & np.any(array[1][t] != (-1000, -1000)):
                    if scen == 0:
                        decision = random.randint(0, (7-agents[a].goal))
                        if decision < 3:
                            array[1][t] = btargets[t].position
                            pagent1T[t] = btargets[t].position
                        else:
                            array[1][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent1T[t] = (random.randint(10, 90), random.randint(10, 90))
                    elif scen == 1:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 4:
                            if agents[a].otrust[1] > 60:
                                array[1][t] = btargets[t].position
                                pagent1T[t] = btargets[t].position
                                if np.any(temp1 != pagent1T[t]):
                                    agents[1].otrust[a] += 1
                                temp1 = array[1][t]
                        else:
                            array[1][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent1T[t] = (random.randint(10, 90), random.randint(10, 90))
                            if np.any(temp != pagent1T[t]):
                                agents[1].otrust[a] -= 1
                            temp1 = array[1][t]
                    else:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 5 & (abs(agents[4].goal - agents[a].goal) > 2):
                            if agents[a].otrust[1] > 60:
                                array[1][t] = btargets[t].position
                                pagent1T[t] = btargets[t].position
                                if np.any(temp != pagent1T[t]):
                                    agents[1].otrust[a] += 1
                                temp1 = array[1][t]

                if distance.euclidean(agents[2].get_head_position(), ctargets[t].position) < 10:
                    agents[2].collected[t] = ctargets[t].position
                    ctargets[t].collected()
                    array[2][t] = ctargets[t].position
                    ctargets[t].position = (-1000, -1000)
                    agents[2].goal += 1
                if (distance.euclidean(agents[a].get_head_position(), ctargets[t].position) < 10) \
                        & np.any(array[2][t] != (-1000, -1000)):
                    if scen == 0:
                        decision = random.randint(0, (7-agents[a].goal))
                        if decision < 3:
                            array[2][t] = ctargets[t].position
                            pagent2T[t] = ctargets[t].position
                        else:
                            array[2][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent2T[t] = (random.randint(10, 90), random.randint(10, 90))
                    elif scen == 1:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 4:
                            if agents[a].otrust[0] > 60:
                                array[2][t] = ctargets[t].position
                                pagent2T[t] = ctargets[t].position
                                if np.any(temp1 != pagent2T[t]):
                                    agents[2].otrust[a] += 1
                                temp2 = array[2][t]
                        else:
                            array[2][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent2T[t] = (random.randint(10, 90), random.randint(10, 90))
                            if np.any(temp1 != pagent2T[t]):
                                agents[2].otrust[a] -= 1
                            temp2 = array[2][t]
                    else:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 5 & (abs(agents[2].goal - agents[a].goal) > 2):
                            if agents[a].otrust[0] > 60:
                                array[2][t] = ctargets[t].position
                                pagent2T[t] = ctargets[t].position
                                if np.any(temp2 != pagent2T[t]):
                                    agents[2].otrust[a] += 1
                                temp2 = array[2][t]
                if distance.euclidean(agents[3].get_head_position(), dtargets[t].position) < 10:
                    agents[3].collected[t] = dtargets[t].position
                    dtargets[t].collected()
                    array[3][t] = dtargets[t].position
                    dtargets[t].position = (-1000, -1000)
                    agents[3].goal += 1
                if (distance.euclidean(agents[a].get_head_position(), dtargets[t].position) < 10) \
                        & np.any(array[3][t] != (-1000, -1000)):
                    if scen == 0:
                        decision = random.randint(0, (7-agents[a].goal))
                        if decision < 3:
                            array[3][t] = dtargets[t].position
                            pagent3T[t] = dtargets[t].position
                        else:
                            array[3][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent3T[t] = (random.randint(10, 90), random.randint(10, 90))
                    elif scen == 1:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 4:
                            if agents[a].otrust[3] > 60:
                                array[3][t] = dtargets[t].position
                                pagent3T[t] = dtargets[t].position
                                if np.any(temp3 != pagent3T[t]):
                                    agents[3].otrust[a] += 1
                                temp3 = array[3][t]
                        else:
                            array[3][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent3T[t] = (random.randint(10, 90), random.randint(10, 90))
                            if np.any(temp3 != pagent3T[t]):
                                agents[3].otrust[a] -= 1
                            temp3 = array[3][t]
                    else:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 5 & (abs(agents[3].goal - agents[a].goal) > 2):
                            if agents[a].otrust[3] > 60:
                                array[3][t] = dtargets[t].position
                                pagent3T[t] = dtargets[t].position
                                if np.any(temp3 != pagent3T[t]):
                                    agents[3].otrust[a] += 1
                                temp3 = array[3][t]
                if distance.euclidean(agents[4].get_head_position(), etargets[t].position) < 10:
                    agents[4].collected[t] = etargets[t].position
                    etargets[t].collected()
                    array[4][t] = etargets[t].position
                    etargets[t].position = (-1000, -1000)
                    agents[4].goal += 1
                if (distance.euclidean(agents[a].get_head_position(), etargets[t].position) < 10) \
                        & np.any(array[4][t] != (-1000, -1000)):
                    if scen == 0:
                        decision = random.randint(0, (7-agents[a].goal))
                        if decision < 2:
                            array[4][t] = etargets[t].position
                            pagent4T[t] = etargets[t].position
                        else:
                            array[4][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent4T[t] = (random.randint(10, 90), random.randint(10, 90))
                    elif scen == 1:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 4:
                            if agents[a].otrust[4] > 60:
                                array[4][t] = etargets[t].position
                                pagent4T[t] = etargets[t].position
                                if np.any(temp4 != pagent4T[t]):
                                    agents[4].otrust[a] += 1
                                temp4 = array[4][t]
                        else:
                            array[4][t] = (random.randint(10, 90), random.randint(10, 90))
                            pagent4T[t] = (random.randint(10, 90), random.randint(10, 90))
                            if np.any(temp4 != pagent4T[t]):
                                agents[4].otrust[a] -= 1
                            temp4 = array[4][t]
                    else:
                        decision = random.randint(0, (7 - agents[a].goal))
                        if decision < 5 & (abs(agents[4].goal - agents[a].goal) > 2):
                            if agents[a].otrust[4] > 60:
                                array[4][t] = etargets[t].position
                                pagent4T[t] = etargets[t].position
                                if np.any(temp4 != pagent4T[t]):
                                    agents[4].otrust[a] += 1
                                temp4 = array[4][t]

    def check_movement():
        if scen == 0:
            for t in range(len(atargets)):
                if (np.any(pagentT[t] != (-1000, -1000))) & (np.any(pagentT[t] != (0, 0))) \
                        & (np.any(agent.collected[t] == (0, 0))) & agent.gtrust >= 55:
                    agent.state = 1
                    agent.rt = t
                    agent.reacht = pagentT[t]
                if (distance.euclidean(agent.get_head_position(), agent.reacht) < 9) & (np.any(agent.collected[t] != (-1000,-1000))):
                    agent.gtrust -= 5
                    agent.state = 0
                elif (distance.euclidean(agent.get_head_position(), agent.reacht) < 9) & (np.any(agent.collected[t] == (-1000,-1000))):
                    agent.gtrust += 5
                    agent.state = 0
            for t in range(len(btargets)):
                if (np.any(pagent1T[t] != (-1000, -1000))) & (np.any(pagent1T[t] != (0, 0))) \
                        & np.any(agent1.collected[t] == (0, 0)) & agent1.gtrust >= 55:
                    agent1.state = 1
                    agent1.rt = t
                    agent1.reacht = pagent1T[t]
                if (distance.euclidean(agent1.get_head_position(), agent1.reacht) < 9) & (
                        np.any(agent1.collected[t] != (-1000, -1000))):
                    agent1.state = 0
                    agent1.gtrust -= 5
                elif (distance.euclidean(agent.get_head_position(), agent1.reacht) < 9) & (
                        np.any(agent1.collected[t] == (-1000, -1000))):
                    agent1.gtrust += 5
                    agent1.state = 0
            for t in range(len(ctargets)):
                if (np.any(pagent2T[t] != (-1000, -1000))) & (np.any(pagent2T[t] != (0, 0))) \
                        & np.any(agent2.collected[t] == (0, 0)) & agent2.gtrust >= 55:
                    agent2.state = 1
                    agent2.rt = t
                    agent2.reacht = pagent2T[t]
                if (distance.euclidean(agent2.get_head_position(), agent2.reacht) < 9) & (
                        np.any(agent2.collected[t] != (-1000, -1000))):
                    agent2.gtrust -= 5
                    agent2.state = 0
                elif (distance.euclidean(agent2.get_head_position(), agent2.reacht) < 9) & (
                        np.any(agent2.collected[t] == (-1000, -1000))):
                    agent2.gtrust += 5
                    agent2.state = 0
            for t in range(len(dtargets)):
                if (np.any(pagent3T[t] != (-1000, -1000))) & (np.any(pagent3T[t] != (0, 0))) \
                        & np.any(agent3.collected[t] == (0, 0)) & agent3.gtrust >= 55:
                    agent3.state = 1
                    agent3.rt = t
                    agent3.reacht = pagent3T[t]
                if (distance.euclidean(agent3.get_head_position(), agent3.reacht) < 9) & (
                        np.any(agent3.collected[t] != (-1000, -1000))):
                    agent3.gtrust -= 5
                    agent3.state = 0
                elif (distance.euclidean(agent3.get_head_position(), agent3.reacht) < 9) & (
                        np.any(agent3.collected[t] == (-1000, -1000))):
                    agent3.gtrust += 5
                    agent3.state = 0
            for t in range(len(etargets)):
                if (np.any(pagent4T[t] != (-1000, -1000))) & (np.any(pagent4T[t] != (0, 0))) \
                        & np.any(agent4.collected[t] == (0, 0)) & agent4.gtrust >= 55:
                    agent4.state = 1
                    agent4.rt = t
                    agent4.reacht = pagent4T[t]
                if (distance.euclidean(agent4.get_head_position(), agent4.reacht) < 9) & (
                        np.any(agent4.collected[t] != (-1000, -1000))):
                    agent4.gtrust -= 5
                    agent4.state = 0
                elif (distance.euclidean(agent4.get_head_position(), agent4.reacht) < 9) & (
                        np.any(agent4.collected[t] == (-1000, -1000))):
                    agent4.gtrust += 5
                    agent4.state = 0
        elif scen == 1:
            for t in range(len(atargets)):
                if (np.any(pagentT[t] != (-1000, -1000))) & (np.any(pagentT[t] != (0, 0))) \
                        & (np.any(agent.collected[t] == (0, 0))) & agent.gtrust >= 55:
                    agent.state = 1
                    agent.rt = t
                    agent.reacht = pagentT[t]
                if (distance.euclidean(agent.get_head_position(), agent.reacht) < 9) & (np.any(agent.collected[t] != (-1000,-1000))):
                    agent.gtrust -= 5
                    agent.state = 0
                elif (distance.euclidean(agent.get_head_position(), agent.reacht) < 9) & (np.any(agent.collected[t] == (-1000,-1000))):
                    agent.gtrust += 5
                    agent.state = 0
            for t in range(len(btargets)):
                if (np.any(pagent1T[t] != (-1000, -1000))) & (np.any(pagent1T[t] != (0, 0))) \
                        & np.any(agent1.collected[t] == (0, 0)) & agent1.gtrust >= 55:
                    agent1.state = 1
                    agent1.rt = t
                    agent1.reacht = pagent1T[t]
                if (distance.euclidean(agent1.get_head_position(), agent1.reacht) < 9) & (
                        np.any(agent1.collected[t] != (-1000, -1000))):
                    agent1.gtrust -= 5
                    agent1.state = 0
                elif (distance.euclidean(agent.get_head_position(), agent1.reacht) < 9) & (
                        np.any(agent1.collected[t] == (-1000, -1000))):
                    agent1.gtrust += 5
                    agent1.state = 0
            for t in range(len(ctargets)):
                if (np.any(pagent2T[t] != (-1000, -1000))) & (np.any(pagent2T[t] != (0, 0))) \
                        & np.any(agent2.collected[t] == (0, 0)) & agent2.gtrust >= 55:
                    agent2.state = 1
                    agent2.rt = t
                    agent2.reacht = pagent2T[t]
                if (distance.euclidean(agent2.get_head_position(), agent2.reacht) < 9) & (
                        np.any(agent2.collected[t] != (-1000, -1000))):
                    agent2.gtrust -= 5
                    agent2.state = 0
                elif (distance.euclidean(agent2.get_head_position(), agent2.reacht) < 9) & (
                        np.any(agent2.collected[t] == (-1000, -1000))):
                    agent2.gtrust += 5
                    agent2.state = 0
            for t in range(len(dtargets)):
                if (np.any(pagent3T[t] != (-1000, -1000))) & (np.any(pagent3T[t] != (0, 0))) \
                        & np.any(agent3.collected[t] == (0, 0)) & agent3.gtrust >= 55:
                    agent3.state = 1
                    agent3.rt = t
                    agent3.reacht = pagent3T[t]
                if (distance.euclidean(agent3.get_head_position(), agent3.reacht) < 9) & (
                        np.any(agent3.collected[t] != (-1000, -1000))):
                    agent3.gtrust -= 5
                    agent3.state = 0
                elif (distance.euclidean(agent3.get_head_position(), agent3.reacht) < 9) & (
                        np.any(agent3.collected[t] == (-1000, -1000))):
                    agent3.gtrust += 5
                    agent3.state = 0
            for t in range(len(etargets)):
                if (np.any(pagent4T[t] != (-1000, -1000))) & (np.any(pagent4T[t] != (0, 0))) \
                        & np.any(agent4.collected[t] == (0, 0)) & agent4.gtrust >= 55:
                    agent4.state = 1
                    agent4.rt = t
                    agent4.reacht = pagent4T[t]
                if (distance.euclidean(agent4.get_head_position(), agent4.reacht) < 9) & (
                        np.any(agent4.collected[t] != (-1000, -1000))):
                    agent4.gtrust -= 5
                    agent4.state = 0
                elif (distance.euclidean(agent4.get_head_position(), agent4.reacht) < 9) & (
                        np.any(agent4.collected[t] == (-1000, -1000))):
                    agent4.gtrust += 5
                    agent4.state = 0
        else:
            for t in range(len(atargets)):
                if (np.any(pagentT[t] != (-1000, -1000))) & (np.any(pagentT[t] != (0, 0))) \
                        & (np.any(agent.collected[t] == (0, 0))):
                    agent.state = 1
                    agent.rt = t
                    agent.reacht = pagentT[t]

            for t in range(len(btargets)):
                if (np.any(pagent1T[t] != (-1000, -1000))) & (np.any(pagent1T[t] != (0, 0))) \
                        & np.any(agent1.collected[t] == (0, 0)):
                    agent1.state = 1
                    agent1.rt = t
                    agent1.reacht = pagent1T[t]

            for t in range(len(ctargets)):
                if (np.any(pagent2T[t] != (-1000, -1000))) & (np.any(pagent2T[t] != (0, 0))) \
                        & np.any(agent2.collected[t] == (0, 0)):
                    agent2.state = 1
                    agent2.rt = t
                    agent2.reacht = pagent2T[t]

            for t in range(len(dtargets)):
                if (np.any(pagent3T[t] != (-1000, -1000))) & (np.any(pagent3T[t] != (0, 0))) \
                        & np.any(agent3.collected[t] == (0, 0)):
                    agent3.state = 1
                    agent3.rt = t
                    agent3.reacht = pagent3T[t]

            for t in range(len(etargets)):
                if (np.any(pagent4T[t] != (-1000, -1000))) & (np.any(pagent4T[t] != (0, 0))) \
                        & np.any(agent4.collected[t] == (0, 0)):
                    agent4.state = 1
                    agent4.rt = t
                    agent4.reacht = pagent4T[t]
        if (agent.state == 1) & (agents[0] == agent) & (agent.goal < 5):
            agent.reach()
        elif (agent.state == 0) & (agents[0] == agent) & (agent.goal < 5):
            agent.move()

        if (agent1.state == 1) & (agents[1] == agent1) & (agent1.goal < 5):
            agent1.reach()
        elif (agent1.state == 0) & (agent1 == agents[1]) & (agent1.goal < 5):
            agent1.move()

        if (agent2.state == 1) & (agents[2] == agent2) & (agent2.goal < 5):
            agent2.reach()
        elif (agent2.state == 0) & (agents[2] == agent2) & (agent2.goal < 5):
            agent2.move()

        if (agent3.state == 1) & (agents[3] == agent3) & (agent3.goal < 5):
            agent3.reach()
        elif (agent3.state == 0) & (agents[3] == agent3) & (agent3.goal < 5):
            agent3.move()

        if (agent4.state == 1) & (agents[4] == agent4) & (agent4.goal < 5):
            agent4.reach()
        elif (agent4.state == 0) & (agents[4] == agent4) & (agent4.goal < 5):
            agent4.move()

    def finish():
        cf = np.array([(agents[0].goal/(agents[0].steps + 1)), (agents[1].goal/(agents[1].steps + 1)),
                       (agents[2].goal/(agents[2].steps + 1)), (agents[3].goal/(agents[3].steps + 1)),
                       (agents[4].goal/(agents[4].steps + 1))], np.float64)
        print cf
        print np.min(cf)
        print np.max(cf)
        global scen1i
        global scen1k
        global scen2i
        global scen2k
        global scen3i
        global scen3k
        for ag in range(5):
            a = scen + 1
            b = iter + 1
            c = ag + 1
            d = agents[ag].goal
            e = agents[ag].steps
            f = cf[ag]
            g = np.float64(np.max(cf))
            h = np.float64(np.min(cf))
            i = cf.mean()
            j = cf.std()
            k = (f-h)/(g-h)
            if scen == 0:
                scen1k += k
            elif scen == 1:
                scen2k += k
            else:
                scen3k += k
            with open('g4_1.csv', 'ab') as csvfile:
                fieldnames = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(
                    {'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f, 'g': g, 'h': h, 'i': i, 'j': j, 'k': k})
        if scen == 0:
            scen1i += i
        elif scen == 1:
            scen2i += i
        else:
            scen3i += i
        print("Writing complete")

    while 1:
        pygame.event.pump()
        surface.fill((0, 0, 0))
        check_target(Agent, Target)
        check_movement()
        for d in range(5):
            agents[d].draw(surface)
            atargets[d].draw(surface)
            btargets[d].draw(surface)
            ctargets[d].draw(surface)
            dtargets[d].draw(surface)
            etargets[d].draw(surface)
        font = pygame.font.Font(None, 28)
        pygame.transform.scale(surface, (1000, 800), screen)
        screen.blit(font.render("A:" + str(agent.goal) + "|" + str(agent.steps), 1, (255, 10, 10)), (1, 5))
        screen.blit(font.render("B:" + str(agent1.goal) + "|" + str(agent1.steps), 1, (255, 10, 10)), (90, 5))
        screen.blit(font.render("C:" + str(agent2.goal) + "|" + str(agent2.steps), 1, (255, 10, 10)), (180, 5))
        screen.blit(font.render("D:" + str(agent3.goal) + "|" + str(agent3.steps), 1, (255, 10, 10)), (270, 5))
        screen.blit(font.render("E:" + str(agent4.goal) + "|" + str(agent4.steps), 1, (255, 10, 10)), (360, 5))
        pygame.display.flip()
        pygame.display.update()
        fpsClock.tick(FPS + 1 / 3)
        if scen == 0:
            if agent.goal >= 5 or agent1.goal >= 5 or agent2.goal >= 5 or agent3.goal >= 5 or agent4.goal >= 5:
                finish()
                return
        elif scen == 1:
            if agent.goal >= 5 & agent1.goal >= 5 & agent2.goal >= 5 & agent3.goal >= 5 & agent4.goal >= 5:
                finish()
                return
        else:
            if agent.goal >= 5 or agent1.goal >= 5 or agent2.goal >= 5 or agent3.goal >= 5 or agent4.goal >= 5:
                finish()
                return

if __name__ == '__main__':

    class Option:

        hovered = False

        def __init__(self, text, pos):
            self.text = text
            self.pos = pos
            self.set_rect()
            self.draw()

        def draw(self):
            self.set_rend()
            screen.blit(self.rend, self.rect)

        def set_rend(self):
            self.rend = menu_font.render(self.text, True, self.get_color())

        def get_color(self):
            if self.hovered:
                return (255, 255, 255)
            else:
                return (100, 100, 100)

        def set_rect(self):
            self.set_rend()
            self.rect = self.rend.get_rect()
            self.rect.topleft = self.pos

    def button_check(pos, x, y, x1, y1):
        return pos[0] >= x and pos[0] < x + x1 and pos[1] >= y and pos[1] < y + y1

    # This function will create a nice button with text in it.
    # `sufrace` is like the default 'DISPLAYSURF', `color` is the color of the box
    # `text_color` is the color of the text in the box
    # `x/y` are the co-ords of the button. `width/height` are the dimensions of button
    # `text` is the text for the label.

    def make_button(surface,color,text_color,x,y,width,height,text):
        pygame.draw.rect(surface, (0,0,0),(x-1,y-1,width+2,height+2),1) #makes outline around the box
        pygame.draw.rect(surface, color,(x,y,width,height))#mkes the box

        myfont = pygame.font.SysFont('Arial Black', 15) #creates the font, size 15 (you can change this)
        label = myfont.render(text, 1, text_color) #creates the label
        surface.blit(label, (x+2, y)) #renders the label


    menu_font = pygame.font.Font(None, 40)
    options = [Option("Scenerio 1,2,3 | 10 Iterations (Default)", (220, 105)),
               Option("Scenerio 1,2,3 | 50 Iterations (Default)", (220, 155)),
               Option("Scenerio 1,2,3 | 100 Iterations (Default)", (220, 205)),
               Option("Scenerio 1,2,3 | 10 Iterations (100% Trust)", (210, 255)),
               Option("Scenerio 1,2,3 | 10 Iterations (0% Trust)", (210, 305)),
               Option("QUIT", (250, 355))]
    scen = 0
    while True:
        pygame.event.pump()
        screen.fill((0, 0, 0))
        for option in options:
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True
                if pygame.mouse.get_pressed()[0] & (option.text == "Scenerio 1,2,3 | 10 Iterations (Default)"):
                    scen1i = 0
                    scen1k = 0
                    while scen1_iter < 10:
                        game(scen, scen1_iter)
                        scen1_iter += 1
                        print scen1_iter
                    scen += 1
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': scen, 'Avg i': (scen1i/scen1_iter), 'Avg k': (scen1k/scen1_iter)})
                    while scen2_iter < 10:
                        game(scen, scen2_iter)
                        scen2_iter += 1
                        print scen2_iter
                    scen += 1
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': scen, 'Avg i': (scen2i/scen2_iter), 'Avg k': (scen2k/(scen2_iter*5))})
                    while scen3_iter < 10:
                        game(scen, scen3_iter)
                        scen3_iter += 1
                        print scen3_iter
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': (scen+1), 'Avg i': (scen3i/scen3_iter), 'Avg k': (scen3k/(scen3_iter*5))})
                    scen = 0
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True
                if pygame.mouse.get_pressed()[0] & (option.text == "Scenerio 1,2,3 | 50 Iterations (Default)"):
                    scen1i = 0
                    scen1k = 0
                    while scen2_iter < 50:
                        game(scen, scen2_iter)
                        scen2_iter += 1
                        print scen2_iter
                    scen += 1
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': scen, 'Avg i': (scen2i/scen2_iter), 'Avg k': (scen2k/(scen2_iter*5))})
                    while scen3_iter < 50:
                        game(scen, scen3_iter)
                        scen3_iter += 1
                        print scen3_iter
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': (scen+1), 'Avg i': (scen3i/scen3_iter), 'Avg k': (scen3k/(scen3_iter*5))})
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True
                if pygame.mouse.get_pressed()[0] & (option.text == "Scenerio 1,2,3 | 100 Iterations (Default)"):
                    scen1i = 0
                    scen1k = 0
                    while scen1_iter < 10:
                        game(scen, scen1_iter)
                        scen1_iter += 1
                        print scen1_iter
                    scen += 1
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': scen, 'Avg i': (scen1i/scen1_iter), 'Avg k': (scen1k/scen1_iter)})
                    while scen2_iter < 10:
                        game(scen, scen2_iter)
                        scen2_iter += 1
                        print scen2_iter
                    scen += 1
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': scen, 'Avg i': (scen2i/scen2_iter), 'Avg k': (scen2k/(scen2_iter*5))})
                    while scen3_iter < 10:
                        game(scen, scen3_iter)
                        scen3_iter += 1
                        print scen3_iter
                    with open('g4_2.csv', 'ab') as csvfile:
                        fieldnames = ['Scen #', 'Avg i', 'Avg k']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(
                            {'Scen #': (scen+1), 'Avg i': (scen3i/scen3_iter), 'Avg k': (scen3k/(scen3_iter*5))})
                    scen = 0
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True
                if pygame.mouse.get_pressed()[0] & (option.text == "QUIT"):
                    pygame.quit()
                    sys.exit()

            else:
                option.hovered = False
            option.draw()
        pygame.display.update()
