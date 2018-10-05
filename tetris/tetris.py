import base
import pygame as pg
from pygame.locals import *

import os
import random
import pprint

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FIELD_W = 12
FIELD_H = 19

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
				field[index] = 1
	return [field]


class Tetromino:

	def __init__(self, tiles, start_x, start_y, width, height, color=WHITE):
		self.x = start_x
		self.y = start_y
		self.w = width
		self.h = height
		self.color = color

		self.index = 0
		self.tiles = tiles
		self.matrix = self.tiles[self.index]

	def draw(self, surface):
		for i in range(self.h):
			for j in range(self.w):
				tile = i * self.w + j
				if self.matrix[tile] == 1:
					rect = get_rect(self.x, self.y, i, j)
					pg.draw.rect(surface, self.color, rect)
					pg.draw.rect(surface, WHITE, rect, 1)

	def rotate(self):
		self.index += 1
		if self.index >= len(self.tiles): self.index = 0
		self.matrix = self.tiles[self.index]


class TetrisGame(base.Game):

	WINDOW_WIDTH = 192
	WINDOW_HEIGHT = 304

	DELAY = 40
	INTER = 80

	def setup(self):
		super(TetrisGame, self).setup()
		pg.display.set_caption('Tetris')

		#setting key repeat frequency (delay, interval)
		pg.key.set_repeat(self.DELAY, self.INTER)

		self.last_update = 0

		self.active = self.create_piece('J')
		self.holding = None

		field = create_field(FIELD_W, FIELD_H)
		self.field = Tetromino(field, 0, 0, FIELD_W, FIELD_H, BLUE)

	def event(self, event):
		if event.type == QUIT:
			self.running = False

		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				self.running = False

			elif event.key == K_UP:
				self.active.rotate()
				if self.collides():
					self.active.rotate()
					self.active.rotate()
					self.active.rotate()
			elif event.key == K_DOWN:  self.move( 0, 1)
			elif event.key == K_LEFT:  self.move(-1, 0)
			elif event.key == K_RIGHT: self.move( 1, 0)

	def draw(self):
		self.field.draw(self.surface)
		self.active.draw(self.surface)

	def update(self, time):
		self.last_update += time / self.FPS
		mov_speed = (1 / GAME_SPEED) * self.FPS
		if self.last_update >= mov_speed:
			self.last_update = 0

			self.try_move_or_place()
			#if self.collides():
		# 	if self.collides(K_DOWN):
		# 		self.all_pieces.append(self.active)
		# 		self.active = self.new_piece()

		# 		print(self.is_tetris())

		# 	else:
		# 		self.active.y += BLOCK_SIZE

	def create_piece(self, piece_name):
		if piece_name == 'L':
			tiles =[[0, 1, 0, 0, 1, 0, 0, 1, 1],
					[0, 0, 0, 1, 1, 1, 1, 0, 0],
					[1, 1, 0, 0, 1, 0, 0, 1, 0],
					[0, 0, 1, 1, 1, 1, 0, 0, 0]]
		if piece_name == 'J':
			tiles =[[0, 1, 0, 0, 1, 0, 1, 1, 0],
					[1, 0, 0, 1, 1, 1, 0, 0, 0],
					[0, 1, 1, 0, 1, 0, 0, 1, 0],
					[0, 0, 0, 1, 1, 1, 0, 0, 1]]

		return Tetromino(tiles, 4, 0, 3, 3, GREEN)

	def collides(self):
		piece = self.active
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
						if px == fx and py == fy and pv == fv == 1:
							return True
		return False

	def move(self, x, y):
		self.active.x += x
		self.active.y += y
		if self.collides():
			self.active.x -= x
			self.active.y -= y

	def try_move_or_place(self):
		# move down
		self.active.y += 1
		if self.collides():
			self.active.y -= 1
		
			# place the active piece into the field
			piece = self.active
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
								if pv == 1 and fv == 1:
									raise RuntimeError('position occupied')
								elif pv == 1 and fv == 0:
									f_index = f_row * field.w + f_col
									field.matrix[f_index] = 1
			self.active = self.create_piece('L')

	def has_rect_in(self, row, col, piece):
		for r in piece.get_rects():
			x = r.x // BLOCK_SIZE
			y = r.y // BLOCK_SIZE
			if x == col and y == row:
				return r
		return None

	def is_occupied(self, row, col):
		for piece in self.all_pieces:
			for r in piece.get_rects():
				rx = r.x // BLOCK_SIZE
				ry = r.y // BLOCK_SIZE
				if rx == col and ry == row:
					return True
		return False

	def is_tetris(self):
		for i in range(1, self.field.w):
			if not self.is_occupied(17, i):
				return False
		for i in range(1, self.field.w):
			for piece in self.all_pieces:
				pass
		return True


if __name__ == '__main__':
	
	game = TetrisGame()
	game.setup()

	print('WxH', FIELD_W, FIELD_H)
	print('GAME SPEED', GAME_SPEED)

	game.loop()