from copy import deepcopy
import arcade
import time

from constants import *


number = 0


def draw_step_on_board(hero, step_coord, current_coord, bfs_board, q):
    x, y = current_coord[0], current_coord[1]
    u, v = step_coord[0], step_coord[1]
    if 0 <= u < len(bfs_board) and 0 <= v < len(bfs_board) and bfs_board[u][v] is None:
        q.append((u, v))
        bfs_board[u][v] = bfs_board[x][y] + 1
    elif 0 <= u < len(bfs_board) and 0 <= v < len(bfs_board) and isinstance(bfs_board[u][v], Hero):
        if bfs_board[u][v].is_enemies(hero):
            return bfs_board[x][y] + 1
    
    return None


def get_distance_from_nearest_enemy(hero, coord, board):
    bfs_board = deepcopy(board)
    bfs_board[coord[0]][coord[1]] = 0
    q = [(coord[0], coord[1])]
    value = None
    while len(q) > 0:
        x, y = q[0][0], q[0][1]
        value = value or draw_step_on_board(hero, (x - 1, y), (x, y), bfs_board, q)
        value = value or draw_step_on_board(hero, (x - 1, y - 1), (x, y), bfs_board, q)
        value = value or draw_step_on_board(hero, (x - 1, y + 1), (x, y), bfs_board, q)
        value = value or draw_step_on_board(hero, (x, y - 1), (x, y), bfs_board, q)
        value = value or draw_step_on_board(hero, (x, y + 1), (x, y), bfs_board, q)
        value = value or draw_step_on_board(hero, (x + 1, y), (x, y), bfs_board, q)
        value = value or draw_step_on_board(hero, (x + 1, y - 1), (x, y), bfs_board, q)
        value = value or draw_step_on_board(hero, (x + 1, y + 1), (x, y), bfs_board, q)

        if value:
            return value
        q.__delitem__(0)
    
    return None


def get_walk_coord(hero, my_coord, board):
    start_x = max(0, my_coord[0] - 1)
    end_x = min(len(board), my_coord[0] + 2)
    start_y = max(0, my_coord[1] - 1)
    end_y = min(len(board), my_coord[1] + 2)
    distance = None
    coord = None
    for i in range(start_x, end_x):
        for j in range(start_y, end_y):
            if not board[i][j]:
                value = get_distance_from_nearest_enemy(hero, (i, j), board)
                if value and (not distance or distance >= value):
                    coord = (i, j)
                    distance = value
    # if hero.number == 7:
    #     print(coord)
    return coord


class Hero(arcade.Sprite):
    def __init__(self, attack_range=1.0, damage=80.0, hp=400.0, armor=5.0, base_attack_time=1.0, attack_speed=100.0, x=0, y=0,
                 in_my_team=True):
        super(Hero, self).__init__()
        global number ##
        number += 1 ##
        self.number = number ##
        self.attack_range = attack_range
        self.current_atack_range = attack_range
        self.base_attack_time = base_attack_time
        self.attack_speed = attack_speed
        self.current_attack_speed = self.attack_speed
        self.max_hp = hp
        self.hp = hp
        self.armor = armor
        self.current_armor = armor
        self.damage = damage
        self.current_damage = damage
        self.attack_time = 100 * self.base_attack_time / self.current_attack_speed
        self.start_x = x
        self.start_y = y
        self.x = x
        self.current_x = x
        self.y = y
        self.current_y = y
        self.in_my_team = in_my_team
        self.last_hit_time = time.time()
        self.last_walk_time = time.time()
        self.ms = 0.5
        self.nearest_enemy = None

    def update_animation(self, delta_time: float = 1 / 60):
        pass

    def draw_hero(self, board_start, box_size):
        center_x = board_start[0] + (self.current_x + 0.5) * box_size
        center_y = board_start[1] + (self.current_y + 0.5) * box_size
        arcade.draw_circle_filled(center_x, center_y, box_size // 3, WHITE if self.in_my_team else RED)
        arcade.draw_text(str(self.number), center_x,
                                  center_y, BLACK)
        
        self.draw_hp(center_x, center_y, box_size)
    
    def draw_hp(self, center_x, center_y, box_size):
        start_x1 = int(center_x - 0.45 * box_size)
        end_x1 = int(start_x1 + 0.9 * box_size * self.hp / self.max_hp)
        start_x2 = end_x1
        end_x2 = int(center_x + 0.45 * box_size)
        y = center_y + 0.4 * box_size
        arcade.draw_line(start_x1, y, end_x1, y, GREEN)
        arcade.draw_line(start_x2, y, end_x2, y, RED)

    def update(self, board, delta_time):
        # if self.nearest_enemy and self.distance(self.nearest_enemy) <= self.current_atack_range:
        #     self.attack(self.nearest_enemy)
        #     return
        if self.x != self.current_x or self.y != self.current_y:
            x_direction = 0
            y_direction = 0
            if self.x != self.current_x:
                x_direction = (self.x - self.current_x) / abs(self.x - self.current_x)
            if self.y != self.current_y:
                y_direction = (self.y - self.current_y) / abs(self.y - self.current_y)
            delta = delta_time / self.ms
            self.current_x += x_direction * delta
            self.current_y += y_direction * delta

            if self.current_x * x_direction >= self.x * x_direction and self.current_y * y_direction >= self.y * y_direction:
                self.current_x = self.x
                self.current_y = self.y
            else:
                return
            
        for row in board:
            for box in row:
                if box and self != box:
                    if self.is_enemies(box):
                        if not self.nearest_enemy or self.distance(box) < self.distance(self.nearest_enemy):
                            self.nearest_enemy = box

        if self.nearest_enemy and self.distance(self.nearest_enemy) <= self.current_atack_range:
            self.attack(self.nearest_enemy)
            if self.nearest_enemy.hp <= 0:
                board[self.nearest_enemy.x][self.nearest_enemy.y] = None
                self.nearest_enemy = None
            return
                    
        if self.nearest_enemy: # walk
            coord = get_walk_coord(self, (self.current_x, self.current_y), board)
            if coord:
                board[self.current_x][self.current_y] = None
                self.x = coord[0]
                self.y = coord[1]
                board[self.x][self.y] = self
                self.last_walk_time = time.time()
    
    def distance(self, enemy):
        return max(abs(self.x - enemy.x), abs(self.y - enemy.y))
    
    def attack(self, enemy):
        if self.last_hit_time + self.attack_time <= time.time():
            self.last_hit_time = time.time()
            enemy.hp -= self.current_damage * (1 - enemy.current_armor / 100)
            if enemy.hp < 0:
                enemy.hp = 0


    def is_enemies(self, hero):
        return not (hero.in_my_team and self.in_my_team) and (hero.in_my_team or self.in_my_team)
