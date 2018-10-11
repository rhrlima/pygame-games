import base
import pygame as pg
from pygame.locals import *

import os
import random

BLACK 	= (  0,   0,   0)
WHITE 	= (255, 255, 255)
GREY 	= (128, 128, 128)
BLUE 	= (  0, 162, 232)
GREEN 	= ( 34, 177,  76)
ORANGE 	= (255, 127,  39)
YELLOW 	= (255, 201,  14)
RED 	= (237,  28,  36)
PINK 	= (255, 174, 201)
PURPLE 	= (163,  73, 164)

COLORS = [BLACK, WHITE, BLUE, GREEN, ORANGE, YELLOW, RED, PINK, PURPLE, GREY]

DELAY = 40
INTER = 80

FIELD_W = 12
FIELD_H = 21

BLOCK_SIZE = 16

GAME_SPEED = 1 # [1:10] every 1 second


def get_rect(x, y, i, j):
	return Rect(
		(x + j) * BLOCK_SIZE,
		(y + i) * BLOCK_SIZE,
		BLOCK_SIZE,
		BLOCK_SIZE
	)


def create_field(w, h):
	field = [0] * w * h
	for row in range(h):
		for col in range(w):
			index = row * w + col
			if col == 0 or col == w-1 or row == h-1:
				field[index] = 9
	return [field]


class Tetromino:

	def __init__(self, tiles, start_x, start_y, width, height):
		self.x = start_x
		self.y = start_y
		self.w = width
		self.h = height

		self.index = 0
		self.tiles = tiles
		self.matrix = self.tiles[self.index]

	def draw(self, surface):
		for i in range(self.h):
			for j in range(self.w):
				tile = i * self.w + j
				value = self.matrix[tile]
				if value > 0:
					rect = get_rect(self.x, self.y, i, j)
					pg.draw.rect(surface, COLORS[value], rect)
					pg.draw.rect(surface, WHITE, rect, 1)

	def rotate(self):
		self.index += 1
		if self.index >= len(self.tiles): self.index = 0
		self.matrix = self.tiles[self.index]


class TetrisGame(base.Game):

	WINDOW_WIDTH  = 288  # 17 blocks
	WINDOW_HEIGHT = 304  # 19 blocks 

	font = None

	game_over = False

	last_update = 0
	active_piece = None
	next_piece = None
	holding = None

	points = 0

	def setup(self):
		super(TetrisGame, self).setup()
		pg.display.set_caption('Tetris')

		#setting key repeat frequency (delay, interval)
		pg.key.set_repeat(DELAY, INTER)

		self.font = pg.font.Font('resources/fonts/base.ttf', 16)

		self.active_piece 	= self.create_piece(next_piece=False)
		self.next_piece = self.create_piece()

		f = create_field(FIELD_W, FIELD_H)
		self.field = Tetromino(f, 0, -2, FIELD_W, FIELD_H)

	def event(self, event):

		if event.type == QUIT:
			self.running = False

		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				self.running = False

			elif event.key == K_SPACE:
				self.hold_piece()

			elif event.key == K_UP:
				self.active_piece.rotate()
				if self.collides():
					self.active_piece.rotate()
					self.active_piece.rotate()
					self.active_piece.rotate()
			elif event.key == K_DOWN:  self.try_move( 0, 1)
			elif event.key == K_LEFT:  self.try_move(-1, 0)
			elif event.key == K_RIGHT: self.try_move( 1, 0)

	def draw(self):

		self.text = self.font.render('{:0>9}'.format(self.points), False, WHITE)
		self.surface.blit(self.text, (200, 4) )

		self.field.draw(self.surface)
		self.active_piece.draw(self.surface)

		self.next_piece.draw(self.surface)
		if self.holding: self.holding.draw(self.surface)

		# next piece
		x = 13; y = 2
		r = Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE*4, BLOCK_SIZE*4)
		pg.draw.rect(self.surface, WHITE, r, 1)

		# holding piece
		x = 13; y = 8
		r = Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE*4, BLOCK_SIZE*4)
		pg.draw.rect(self.surface, WHITE, r, 1)

	def update(self, time):

		if self.game_over:
			print('GAME OVER')
			self.running = False
			# go to game over scene

		self.last_update += time / self.FPS
		mov_speed = (1 / GAME_SPEED) * self.FPS
		if self.last_update >= mov_speed:
			self.last_update = 0
			self.try_move_or_place()
			self.check_tetris()
			self.check_game_over()

	def create_piece(self, piece_name=None, next_piece=True):
		pieces = ['L', 'J', 'S', 'Z', 'T', 'O', 'I']
		w = 3
		h = 3
		if not piece_name: piece_name = random.choice(pieces)
		if piece_name == 'L':
			tiles =[[0, 2, 0, 0, 2, 0, 0, 2, 2],
					[0, 0, 0, 2, 2, 2, 2, 0, 0],
					[2, 2, 0, 0, 2, 0, 0, 2, 0],
					[0, 0, 2, 2, 2, 2, 0, 0, 0]]
		if piece_name == 'J':
			tiles =[[0, 3, 0, 0, 3, 0, 3, 3, 0],
					[3, 0, 0, 3, 3, 3, 0, 0, 0],
					[0, 3, 3, 0, 3, 0, 0, 3, 0],
					[0, 0, 0, 3, 3, 3, 0, 0, 3]]
		if piece_name == 'S':
			tiles =[[0, 4, 4, 4, 4, 0, 0, 0, 0],
					[4, 0, 0, 4, 4, 0, 0, 4, 0]]
		if piece_name == 'Z':
			tiles =[[5, 5, 0, 0, 5, 5, 0, 0, 0],
					[0, 0, 5, 0, 5, 5, 0, 5, 0]]
		if piece_name == 'T':
			tiles =[[0, 0, 0, 6, 6, 6, 0, 6, 0],
					[0, 6, 0, 6, 6, 0, 0, 6, 0],
					[0, 6, 0, 6, 6, 6, 0, 0, 0],
					[0, 6, 0, 0, 6, 6, 0, 6, 0]]
		if piece_name == 'O':
			tiles =[[7, 7, 7, 7]]
			w = 2; h = 2
		if piece_name == 'I':
			tiles =[[0, 8, 0, 0, 0, 8, 0, 0, 0, 8, 0, 0, 0, 8, 0, 0],
					[0, 0, 0, 0, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0]]
			w = 4; h =4

		x = 4; y = -2
		if next_piece:
			x = 13; y = 2
		return Tetromino(tiles, x, y, w, h)

	def get_next_piece(self):
		self.active_piece = self.next_piece
		self.active_piece.x = 4
		self.active_piece.y = -2
		self.next_piece = self.create_piece()

	def hold_piece(self):
		if self.holding == None:
			self.holding = self.active_piece
			self.get_next_piece()

			self.active_piece.x = self.holding.x
			self.active_piece.y = self.holding.y
		else:
			temp = self.active_piece
			self.active_piece = self.holding
			self.active_piece.x = temp.x
			self.active_piece.y = temp.y
			self.holding = temp

		self.holding.x = 13
		self.holding.y = 8

		if self.collides():
			self.hold_piece()

	def collides(self):
		piece = self.active_piece
		field = self.field
		for p_row in range(piece.h):
			for p_col in range(piece.w):
				px = piece.x + p_col
				py = piece.y + p_row
				pv = piece.matrix[p_row * piece.w + p_col]
				for f_row in range(field.h):
					for f_col in range(field.w):
						fx = field.x + f_col
						fy = field.y + f_row
						fv = field.matrix[f_row * field.w + f_col]
						if px == fx and py == fy and pv > 0 and fv > 0:
							return True
		return False

	def try_move(self, x, y):
		self.active_piece.x += x
		self.active_piece.y += y
		if self.collides():
			self.active_piece.x -= x
			self.active_piece.y -= y

	def try_move_or_place(self):
		# move down
		self.active_piece.y += 1
		if self.collides():
			self.active_piece.y -= 1
		
			# place the active_piece piece into the field
			piece = self.active_piece
			field = self.field
			for p_row in range(piece.h):
				for p_col in range(piece.w):
					px = piece.x + p_col
					py = piece.y + p_row
					pv = piece.matrix[p_row * piece.w + p_col]
					for f_row in range(field.h):
						for f_col in range(field.w):
							fx = field.x + f_col
							fy = field.y + f_row
							fv = field.matrix[f_row * field.w + f_col]
							if px == fx and py == fy:
								if pv > 0 and fv == 0:
									f_index = f_row * field.w + f_col
									field.matrix[f_index] = pv
			self.get_next_piece()

	def check_tetris(self):
		tetris = [True] * (self.field.h-1)
		for row in range(0, self.field.h-1):
			for col in range(1, self.field.w-1):
				index = row * self.field.w + col
				if self.field.matrix[index] == 0:
					tetris[row] = False
					break

		tetris_count = sum(tetris)
		self.add_points(100 * tetris_count)
		
		for row in range(0, self.field.h-1):
			if tetris[row]:
				index = row * self.field.w
				del self.field.matrix[index:index + self.field.w]
				new_line = [9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9]
				self.field.matrix = new_line + self.field.matrix

	def check_game_over(self):
		if sum(self.field.matrix[1:11]) > 0:
			self.game_over = True

	def add_points(self, amount):
		global GAME_SPEED

		if self.points < 5000:
			GAME_SPEED = 1
		elif self.points >= 5000 and self.points < 10000:
			GAME_SPEED = 2
		elif self.points >= 10000 and self.points < 25000:
			GAME_SPEED = 3
			amount *= 2
		elif self.points >= 25000 and self.points < 50000:
			GAME_SPEED = 4
			amount *= 5
		elif self.points >= 75000 and self.points < 100000:
			GAME_SPEED = 5
			amount *= 10
		elif self.points >= 200000 and self.points < 300000:
			GAME_SPEED = 6
			amount *= 20
		elif self.points >= 300000 and self.points < 500000:
			GAME_SPEED = 7
			amount *= 25
		else:
			amount *= 50
			GAME_SPEED = 8

		self.points += amount


if __name__ == '__main__':
	
	game = TetrisGame()
	game.setup()
	game.loop()