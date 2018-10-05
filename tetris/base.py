import pygame as pg
from pygame.locals import *

class Game:

	WINDOW_WIDTH  = 400
	WINDOW_HEIGHT = 400
	FPS = 30

	def __init__(self):
		self.surface = None
		self.clock = None
		self.running = None

	def setup(self):
		pg.init()
		pg.display.set_caption("base window")
		self.surface = pg.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pg.HWSURFACE)
		self.clock = pg.time.Clock()
		self.running = True

	def teardown(self):
		pg.quit()
		quit()

	def event(self, event):
		if event.type == QUIT:
			self.running = False
		print(event)

	def update(self, time):
		# Does nothing by default
		pass
	
	def draw(self):
		# Does nothing by default
		pass
	
	def loop(self):
		while self.running:
			time = self.clock.tick(self.FPS)
			for event in pg.event.get():
				self.event(event)

			self.surface.fill((0, 0, 0)) # fills the screen with black
			
			self.update(time)
			self.draw() # draws the child behavior
			
			pg.display.flip() # updates de screen

		self.teardown()