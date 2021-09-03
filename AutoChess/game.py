import arcade
# import random
# import pygame
import math
# import time
# from copy import deepcopy
from constants import *
from hero import Hero


class Rectangle:
    def __init__(self, center_x, center_y, width, height, color, is_filled=True):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.color = color
        self.is_filled = is_filled
    
    def draw(self):
        if self.is_filled:
            arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, self.color)
        else:
            arcade.draw_rectangle_outline(self.center_x, self.center_y, self.width, self.height, self.color, 2)


class Button:
    def __init__(self, center_x, center_y, width, height, color, hover_color, is_filled=True):
        self.shape = Rectangle(center_x, center_y, width, height, color, is_filled)
        self.shape_hover = Rectangle(center_x, center_y, width, height, hover_color, is_filled)
        self.is_hover = False
    
    def is_hovered(self, mouse_x, mouse_y):
        if self.shape.center_x - self.shape.width / 2 <= mouse_x <= self.shape.center_x + self.shape.width / 2 and \
            self.shape.center_y - self.shape.height / 2 <= mouse_y <= self.shape.center_y + self.shape.height / 2:
            self.is_hover = True
        else:
            self.is_hover = False
        
        return self.is_hover
    
    def draw(self):
        if self.is_hover:
            self.shape_hover.draw()
        else:
            self.shape.draw()
        arcade.draw_text("Start", self.shape.center_x, self.shape.center_y, BLACK, anchor_x="center", anchor_y="center")


class GameWindow(arcade.Window):
    def __init__(self):
        super(GameWindow, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Game", True)
        arcade.set_background_color(GRAY)
        self.box_count = 6
        self.box_size = int(SCREEN_HEIGHT * 0.9 / self.box_count)
        self.board_start_x = int(SCREEN_WIDTH / 2 - self.box_size * self.box_count / 2)
        self.board_start_y = int(SCREEN_HEIGHT / 2 - self.box_size * self.box_count / 2)
        self.board_end_x = self.board_start_x + self.box_size * self.box_count
        self.board_end_y = self.board_start_y + self.box_size * self.box_count
        self.board = [[None] * self.box_count for _ in range(self.box_count)]
        self.my_team = None
        self.enemy_team = None
        self.selected_hero = None
        self.info_board = Rectangle(self.board_start_x / 3, SCREEN_HEIGHT / 2, 2 / 3 * self.board_start_x, SCREEN_HEIGHT, SILVER)
        self.max_hp_info_rect = Rectangle(self.info_board.center_x, self.info_board.center_y, 
            self.info_board.width / 2, SCREEN_HEIGHT / 30, GREEN)
        self.hp_info_rect = Rectangle(0, self.max_hp_info_rect.center_y, 0, self.max_hp_info_rect.height, RED)
        self.start_button = Button(SCREEN_WIDTH / 2, (self.board_end_y + SCREEN_HEIGHT) / 2, 
            SCREEN_WIDTH / 10, (SCREEN_HEIGHT - self.board_end_y) / 1.5, GREEN, GREEN_YELLOW)
        self.info_distance = SCREEN_HEIGHT / 20
        self.round_start = False
        self.start_button.hover = False

    def setup(self):
        # self.my_team = [Hero()]
        self.round_start = False
        self.my_team = [Hero(), Hero(x=1), Hero(x=5), Hero(x=2), Hero(x=3)]
        # self.enemy_team = [Hero(y=5, in_my_team=False)] 
        self.enemy_team = [Hero(y=5, in_my_team=False), Hero(y=5, x=5, in_my_team=False), 
            Hero(y=5, x=4, in_my_team=False), Hero(y=5, x=3, in_my_team=False), Hero(y=5, x=1, in_my_team=False)]
        for hero in self.my_team + self.enemy_team:
            self.board[hero.current_x][hero.current_y] = hero

    def on_draw(self):
        arcade.start_render()
        self.draw_board()
        self.draw_hero_info()
        for character in self.my_team + self.enemy_team:
            if character.hp > 0:
                character.draw_hero((self.board_start_x, self.board_start_y), self.box_size)
        
        if not self.round_start:
            self.start_button.draw()
    
    def draw_hero_info(self):
        if not self.selected_hero:
            return
        self.info_board.draw()
        self.max_hp_info_rect.draw()
        self.hp_info_rect.width = ( 1 - self.selected_hero.hp / self.selected_hero.max_hp ) * self.max_hp_info_rect.width
        self.hp_info_rect.center_x = self.max_hp_info_rect.center_x + ( self.max_hp_info_rect.width - self.hp_info_rect.width) / 2
        self.hp_info_rect.draw()
        arcade.draw_text(f"{int(self.selected_hero.hp)}/{int(self.selected_hero.max_hp)}", self.max_hp_info_rect.center_x, 
            self.max_hp_info_rect.center_y, BLACK, anchor_x="center", anchor_y="center")
        arcade.draw_text(f"Damage: {int(self.selected_hero.current_damage)}", self.max_hp_info_rect.center_x, self.max_hp_info_rect.center_y - self.info_distance, 
            BLACK, anchor_x="center", anchor_y="center")
        arcade.draw_text(f"Attack speed: {int(self.selected_hero.current_attack_speed)}", self.max_hp_info_rect.center_x, self.max_hp_info_rect.center_y - 2 * self.info_distance, 
            BLACK, anchor_x="center", anchor_y="center")
        arcade.draw_text(f"Armor: {self.selected_hero.current_armor}", self.max_hp_info_rect.center_x, self.max_hp_info_rect.center_y - 3 * self.info_distance, 
            BLACK, anchor_x="center", anchor_y="center")

    def draw_board(self):
        for i in range(self.box_count + 1):
            arcade.draw_line(self.board_start_x, self.board_start_y + i * self.box_size,
                             self.board_end_x, self.board_start_y + i * self.box_size, BLACK)
            arcade.draw_line(self.board_start_x + i * self.box_size, self.board_start_y,
                             self.board_start_x + i * self.box_size, self.board_end_y, BLACK)

    def update(self, delta_time: float = 1/60):
        if self.round_start:
            for character in self.enemy_team + self.my_team:
                if character.hp > 0:
                    character.update(self.board, delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if not self.round_start:
            if self.start_button.is_hovered(x, y):
                pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if not self.round_start and self.start_button.is_hovered(x, y):
            self.round_start = True
        for character in self.my_team + self.enemy_team:
            if character.hp <= 0:
                continue
            center_x = self.board_start_x + (character.current_x + 0.5) * self.box_size
            center_y = self.board_start_y + (character.current_y + 0.5) * self.box_size
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= self.box_size // 3:
                self.selected_hero = character
                return
        
        self.selected_hero = None


window = GameWindow()
window.setup()
arcade.set_window(window)
arcade.run()
