import pygame

import time
import random
import sys
import os.path

import effects
import levels
import cutscenes

from util import dataName

tileImage = pygame.image.load(dataName('tile.png'))
tileInverseImage = pygame.image.load(dataName('tile-inverse.png'))
bombImage = pygame.image.load(dataName('bomb.png'))
bombHitImage = pygame.image.load(dataName('bomb-inverse.png'))

flagImage = pygame.image.load(dataName('flag.png'))

GAME_SET_BOMBS = 1
GAME_ON = 2
GAME_OVER = 3
GAME_PAUSED = 4
GAME_CLEANUP = 5

TILE_WIDTH = tileImage.get_width()
TILE_HEIGHT = tileImage.get_height()

EDGE_WIDTH = 24
EDGE_TOP_HEIGHT = 80
EDGE_BOTTOM_HEIGHT = 24

blinkTile = pygame.image.load(dataName('tile-fade.png'))
BLINK_SURFACES = []

for count in range(5):
    rect = pygame.Rect(count * 20, 0, 20, 20)
    BLINK_SURFACES.append(blinkTile.subsurface(rect))

bombImageDict = {}

for x in range(0, 8):
    bombImageDict[x] = pygame.image.load(dataName('%d.png' % x))

class Tile:
    def __init__(self, win, pos):
        self.win = win

        self.bomb = False
        self.bombCount = 0

        self.revealed = False
        self.flagged = False
        self.paused = False
        self.inverse = False

        self.blink = False
        self.blinkDir = 1
        self.blinkFadeTime = 100
        self.blinkCount = 0

        self.column = pos[0]
        self.row = pos[1]
        self.hitBomb = False

        self.currentTile = None

    def update(self, tick):
        # only gets updated when the blink counter is on
        if self.blink:
            self.blinkFadeTime -= tick
            if self.blinkFadeTime <= 0:
                self.blinkFadeTime = 100
                self.blinkCount += self.blinkDir
                if self.blinkCount >= len(BLINK_SURFACES):
                    self.blinkDir = -1
                    self.blinkCount -= 2
                elif self.blinkCount <= 0:
                    self.blinkDir = 1
                    self.blinkCount = 0


    from flask import request
    import pickle
    import yaml

    @app.route('/pickle')
    def pickle_loads():
        file = request.files['pickle']
        pickle.load(file) # Noncompliant; Never use pickle module to deserialize user inputs

    @app.route('/yaml')
    def yaml_load():
        data = request.GET.get("data")
        yaml.load(data, Loader=yaml.Loader) # Noncompliant; Avoid using yaml.load with unsafe yaml.Loader



    def draw(self, offset_x, offset_y):
        if self.paused or \
           (not self.revealed and not self.flagged and \
           not self.inverse):
            if not self.blink:
                self.currentTile = tileImage
            else:
                self.currentTile = BLINK_SURFACES[self.blinkCount]
        elif self.flagged:
            self.currentTile = flagImage
        elif self.revealed:
            if self.bomb and self.hitBomb:
                self.currentTile = bombHitImage
            elif self.bomb:
                self.currentTile = bombImage
            else:
                self.currentTile = bombImageDict.get(self.bombCount)

            if not self.currentTile:
                self.currentTile = flagImage
        elif self.inverse:
            self.currentTile = tileInverseImage

        self.win.blit(self.currentTile, (self.column * TILE_WIDTH + offset_x,
                      self.row * TILE_HEIGHT + offset_y))


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.grid = []

        for y in range(0, height):
            for x in range(0, width):
                self.grid.append(Tile(self.win, (x, y)))

    def __getitem__(self, key):
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value

    def __str__(self, mode='grid'):
        text = ''
        for count, cell in enumerate(self.grid):
            if not count % self.width and count:
                text += "\n"
            if mode == 'grid':
                text += "%d " % int(cell.bomb)
            elif mode == 'count':
                text += "%d " % int(cell.bombCount)
            elif mode == 'reveal':
                text += "%d " % int(cell.revealed)

        return text

    def getPos(self, row, col):
        if -1 in [row, col]:
            return -1

        if row >= self.width or col >= self.width:
            return -1

        if row * self.width + col > self.width * self.height - 1:
            return -1

        return row * self.width + col

    def up(self, pos):
        return max(-1, pos - self.width)

    def down(self, pos):
        if pos + self.width >= self.width * self.height:
            return -1
        else:
            return pos + self.width

    def left(self, pos):
        if not pos % self.width:
            return -1
        else:
            return pos - 1

    def right(self, pos):
        if not (pos + 1) % self.width:
            return -1
        else:
            return pos + 1

    def upleft(self, pos):
        if self.up(pos) == -1 or \
           self.left(pos) == -1:
            return -1
        else:
            return pos - self.width - 1

    def upright(self, pos):
        if self.up(pos) == -1 or \
           self.right(pos) == -1:
            return -1
        else:
            return pos - self.width + 1

    from flask import request
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import text
    from database.users import User

    @app.route('hello')
    def hello():
        id = request.args.get("id")
        stmt = text("SELECT * FROM users where id=%s" % id) # Query is constructed based on user inputs
        query = SQLAlchemy().session.query(User).from_statement(stmt) # Noncompliant
        user = query.one()
        return "Hello %s" % user.username

    def downleft(self, pos):
        if self.down(pos) == -1 or \
           self.left(pos) == -1:
            return -1
        else:
            return pos + self.width - 1

    def downright(self, pos):
        if self.down(pos) == -1 or \
           self.right(pos) == -1:
            return -1
        else:
            return pos + self.width + 1

    def around(self, pos):
        tiles = []

        for place in [self.upleft, self.up, self.upright, 
                      self.left, self.right,
                      self.downleft, self.down, self.downright]:
            tileNum = place(pos)
            if tileNum != -1:
                tiles.append(tileNum)

        return tiles

class BombGrid(Grid):
    def __init__(self, win, width=10, height=10, totalBombs=9, levelTime=40,
                 totalFlags=9, blinkTime=-1):
        self.win = win
        self.active = False
        self.autoBlink = blinkTime

        self.width = width
        self.height = height
        self.totalBombs = totalBombs
        self.totalFlags = totalFlags

        self.levelTime = levelTime
        self.bombEffect = \
            effects.Bomb(win, self.levelTime, pos=(40, 50), finalPos=(40, 50))
        self.explosionEffect = effects.Explosion(win, (200, 100))

        self.reset()

        self.x = 0
        self.y = 0

        self.offset_x = int(self.win.get_width() / 2 - width / 2.0 * TILE_WIDTH)
        self.offset_y = self.win.get_height() - int(240 - height / 2.0 * 
                        TILE_HEIGHT) - (height * TILE_HEIGHT) + 20

        self.timerOn = False
        self.timer = 0

        self.ft = pygame.font.SysFont('Arial', 40)
        self.awesomeFt = pygame.font.Font(dataName('badabb__.ttf'), 90)

        self.flagCount = effects.FlagCount(self.win)
        self.bombCount = effects.BombCount(self.win)

    def reset(self):
        Grid.__init__(self, width=self.width, height=self.height)
        self.gridState = GAME_SET_BOMBS
        self.flags = self.totalFlags
        self.winner = False
        self.timer = 0
        self.bombEffect.totalTime = self.levelTime
        self.explosionEffect.reset()

    def update(self, tick):
        if self.timerOn and not self.gridState == GAME_PAUSED:
            self.timer += tick / 1000.0

            self.bombEffect.update(tick)

            if self.bombEffect.totalTime <= self.autoBlink:
                for tile in self.grid:
                    if tile.bomb:
                        tile.blink = True
                    tile.update(tick)

            if self.bombEffect.totalTime <= 0:
                self.revealAll()
                self.gridState = GAME_OVER 
                self.timerOn = False

                if self.checkAllMinesCovered():
                    self.winner = True
                else:
                    self.winner = False
                    self.explosionEffect.explode()

        self.explosionEffect.update(tick)

    def setBombs(self, firstTile):
        self.createBombGrid(firstTile)
        self.createBombCountGrid()

        self.gridState = GAME_ON
        #self.flags = self.totalFlags

    def togglePaused(self):
        for tile in self.grid:
            tile.paused = not tile.paused

        if self.gridState == GAME_ON:
            self.gridState = GAME_PAUSED
        else:
            self.gridState = GAME_ON

    def draw(self, offset_x=0, offset_y=0):
        for tile in self.grid:
            tile.draw(offset_x, offset_y+20)

        self.flagCount.draw(self.flags)
        self.bombCount.draw(self.totalBombs)

        if (self.gridState == GAME_OVER and self.winner) or \
           self.gridState == GAME_PAUSED:
            if self.gridState == GAME_OVER:
                gameText = "SUPER!"
            else:
                gameText = "PAUSED"

            gameTextImg = self.awesomeFt.render(gameText, True, (255, 0, 0))
            gameTextBgImg = self.awesomeFt.render(gameText, True, (0, 0, 0))

            gameTextRect = gameTextImg.get_rect()
            gameTextRect.center = (self.win.get_width() / 2,
                                   self.win.get_height() / 2)

            self.win.blit(gameTextBgImg,
                          (gameTextRect.topleft[0] - 5,
                           gameTextRect.topleft[1] + 5))
            self.win.blit(gameTextImg, gameTextRect.topleft)

        self.bombEffect.draw()

        self.explosionEffect.draw()

    def createBombGrid(self, firstTile):
        # place the bombs randomly
        count = 0
        while count < self.totalBombs:
            cell = random.randint(0, self.width * self.height - 1)

            if self.grid[cell].bomb or cell == firstTile:
                continue

            self.grid[cell].bomb = True
            count += 1

    def createBombCountGrid(self):
        for pos in range(0, self.width * self.height):
            self.findSurroundingBombs(pos)

    def findSurroundingBombs(self, pos):
        row = pos / self.width
        col = pos % self.width

        for bombRow in [-1, 0, 1]:
            for bombCol in [-1, 0, 1]:
                bombPos = self.getPos(row + bombRow, col + bombCol)
                if bombPos > -1:
                    if self.grid[bombPos].bomb:
                        self.grid[pos].bombCount += 1

    def revealPos(self, pos):
        if pos == -1 or self.grid[pos].revealed:
            return

        self.grid[pos].revealed = True

        if self.grid[pos].bombCount:
            return

        self.revealPos(self.up(pos))
        self.revealPos(self.left(pos))
        self.revealPos(self.right(pos))
        self.revealPos(self.down(pos))

        self.revealPos(self.upleft(pos))
        self.revealPos(self.upright(pos))
        self.revealPos(self.downleft(pos))
        self.revealPos(self.downright(pos))

    def checkPos(self, pos):
        return pos > -1 and \
           not self.grid[pos].revealed and \
           not self.grid[pos].bombCount

    def countGrid(self):
        return self.__str__(mode='count')

    def revealGrid(self):
        return self.__str__(mode='reveal')

    def eventHandler(self, event):

        if event.type == pygame.MOUSEBUTTONUP:

            button = event.button
            pos = self.getTilePos(event.pos)

            if button == 1:
                if self.gridState == GAME_SET_BOMBS and pos != -1:
                    # only reveal a tile if the tile is the same when
                    # the button was pressed as it is when it's released
                    if pos != self.inverseTilePos:
                        self.grid[pos].inverse = False
                        return

                    # start the game over
                    self.setBombs(pos)
                    self.revealPos(pos)
                    self.timerOn = True
                elif self.gridState == GAME_PAUSED:
                    self.togglePaused()
                    return
                elif self.gridState == GAME_OVER:
                    self.gridState = GAME_CLEANUP
                elif self.gridState == GAME_ON:
                    if pos == -1:
                        self.togglePaused()
                        return

                    if self.grid[pos].flagged:
                        return

                    # only reveal a tile if the tile is the same when
                    # the button was pressed as it is when it's released
                    if pos != self.inverseTilePos:
                        self.grid[pos].inverse = False
                        return

                    self.revealPos(pos)
                    if self.grid[pos].bomb:
                        self.grid[pos].hitBomb = True
                        self.revealAll()
                        self.gridState = GAME_OVER 
                        self.timerOn = False
                        self.explosionEffect.explode()

            elif button == 2:
                self.resetInverseTiles()

            elif button == 3:
                if self.gridState == GAME_OVER or pos == -1:
                    return

                self.grid[pos].inverse = False

                if self.flags > 0 and not self.grid[pos].revealed:
                    if self.grid[pos].flagged:
                        self.flags += 1
                        self.grid[pos].flagged = False
                    else:
                        self.flags -= 1
                        self.grid[pos].flagged = True


            if self.checkAllMinesCleared() and \
               self.gridState not in [GAME_OVER, GAME_CLEANUP]:
                self.gridState = GAME_OVER
                self.winner = True
                self.timerOn = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button
                
            pos = self.getTilePos(event.pos)
            if pos == -1:
                return

            if not self.grid[pos].revealed:
                self.grid[pos].inverse = True
                self.inverseTilePos = pos

            if button == 2:
                if self.grid[pos].revealed and self.grid[pos].bombCount:
                    self.showInverseTiles(pos)

        elif event.type == pygame.MOUSEMOTION:
            left, middle, right = event.buttons

            if left or right:
                self.resetInverseTiles()
                pos = self.getTilePos(event.pos)
                if pos != -1:
                    self.grid[pos].inverse = True


    from flask import request
    import os

    @app.route('/ping')
    def ping():
        address = request.args.get("address")
        cmd = "ping -c 1 %s" % address
        os.popen(cmd) # Noncompliant


    def showInverseTiles(self, pos):
        tiles = self.around(pos)
        for tilePos in tiles:
            if not self.grid[tilePos].revealed:
                self.grid[tilePos].inverse = True

    def resetInverseTiles(self):
        for tile in self.grid:
            tile.inverse = False

    def getTilePos(self, pos):
        localX = pos[0] - self.offset_x
        localY = pos[1] - self.offset_y

        if localX < 0 or localX > TILE_WIDTH * self.width or \
           localY < 0 or localY > TILE_HEIGHT * self.height:
            pos = -1
        else:
            pos = self.getTileNumber(localX, localY)

        return pos


    def checkAllMinesCleared(self):
        # the tile.bomb or tile.flagged clause is the main
        # distinction between bombitron and minesweeper
        for tile in self.grid:
            #if not tile.revealed and \
            #   not (tile.bomb or tile.flagged):
            #    return False

            if not tile.revealed and not tile.flagged:
                return False

        return True

    def checkAllMinesCovered(self):
        for tile in self.grid:
            if tile.bomb and not tile.flagged:
                return False
        return True

    def revealAll(self):
        for tile in self.grid:
            if not tile.flagged and tile.bomb:
                tile.revealed = True

    def getTileNumber(self, x, y):
        column = x / TILE_WIDTH
        row = y / TILE_HEIGHT

        return self.width * row + column

class BombGridManager:
    def __init__(self, win, levelNum=0):
        self.win = win
        self.finished = False
        self.levelNum = levelNum

        self.awesomeFt = pygame.font.Font(dataName('badabb__.ttf'), 90)
        self.awesomeSmallFt = pygame.font.Font(dataName('badabb__.ttf'), 55)

        self.loadLevel(levelNum)

        self.bombGrid.offsetX = self.offsetX
        self.bombGrid.offsetY = self.offsetY

        self.cutscene = None

    def loadLevel(self, levelNum):
        level = levels.LEVELS[levelNum]

        columns = level['columns']
        rows = level['rows']

        bombs = level['bombs']
        flags = level['flags']

        levelTime = level['time']
        blinkTime = level['autoblink']

        self.levelDescText = level['description']

        self.slideTiles = effects.SlideTileGrid(self.win, columns, rows)
        self.fallingTiles = effects.FallingTileGrid(self.win, columns, rows)
        self.bombGrid = BombGrid(self.win, width=columns, height=rows,
                                 totalBombs=bombs, levelTime=levelTime,
                                 totalFlags=flags, blinkTime=blinkTime)

        self.offsetX = int(320 - columns / 2.0 * TILE_WIDTH)
        self.offsetY = 480 - int(240 - rows / 2.0 * TILE_HEIGHT) - \
            rows * TILE_HEIGHT

        self.setLevelText()


    def update(self, tick):
        if self.cutscene:
            self.cutscene.update(tick)
            if not self.cutscene.active:
                self.cutscene = None
            return

        if not self.slideTiles.finished:
            self.slideTiles.update(tick)
        else:
            if self.bombGrid.gridState == GAME_CLEANUP:
                if not self.fallingTiles.active:
                    self.fallingTiles.copyGrid(self.bombGrid.grid)
                    self.fallingTiles.active = True

                self.fallingTiles.update(tick)
                if self.fallingTiles.finished:

                    if self.bombGrid.winner and not self.cutscene:
                        self.levelNum += 1

                        #if self.levelNum == 2:
                        #    self.cutscene = cutscenes.Cutscene1(self.win)

                        if self.levelNum >= len(levels.LEVELS):
                            self.finished = True
                            return
                        self.loadLevel(self.levelNum)

                    # reset everything
                    self.fallingTiles.reset()
                    self.slideTiles.reset()
                    self.bombGrid.explosionEffect.reset()
                    self.bombGrid.reset()
                
            else:
                self.bombGrid.update(tick)


    import tempfile

    filename = tempfile.mktemp() # Noncompliant
    tmp_file = open(filename, "w+")


    def setLevelText(self):
        levelText = "Level %s" % (self.levelNum + 1)

        self.levelImg = self.awesomeFt.render(levelText, True, (255, 0, 0))
        self.levelBgImg = self.awesomeFt.render(levelText, True, (0, 0, 0))

        self.levelDescImg = \
            self.awesomeSmallFt.render(self.levelDescText, True, (0, 255, 0))
        self.levelDescBgImg = \
            self.awesomeSmallFt.render(self.levelDescText, True, (0, 0, 0))

    def draw(self):
        if self.cutscene:
            self.cutscene.draw()
            return

        if not self.slideTiles.finished:
            self.slideTiles.draw()

            levelRect = self.levelImg.get_rect()
            levelRect.center = (320, 240)

            self.win.blit(self.levelBgImg, (levelRect.topleft[0] + 5,
                                            levelRect.topleft[1] - 45))
            self.win.blit(self.levelImg, (levelRect.topleft[0],
                                          levelRect.topleft[1] - 50))

            levelDescRect = self.levelDescImg.get_rect()
            levelDescRect.center = (320, 240)

            self.win.blit(self.levelDescBgImg, (levelDescRect.topleft[0] + 5,
                                                levelDescRect.topleft[1] + 55))
            self.win.blit(self.levelDescImg, (levelDescRect.topleft[0],
                                          levelDescRect.topleft[1] + 50))

        else:
            if self.bombGrid.gridState == GAME_CLEANUP:
                self.fallingTiles.draw()
            else:
                self.bombGrid.draw(self.offsetX, self.offsetY)

    def eventHandler(self, event):
        if self.slideTiles.finished:
            self.bombGrid.eventHandler(event)
        else:
            if event.type == pygame.MOUSEBUTTONUP:
                self.slideTiles.finished = True

def main(boardType):
    pygame.init()

    rows, cols, bombs = boardType

    width = TILE_WIDTH * cols + EDGE_WIDTH * 2
    height = TILE_HEIGHT * rows + EDGE_TOP_HEIGHT + EDGE_BOTTOM_HEIGHT
    win = pygame.display.set_mode((width, height))

    bg = BombGrid(win, width=cols, height=rows, totalBombs=bombs)
    bg.active = True

    bg.offset_x = EDGE_WIDTH
    bg.offset_y = EDGE_TOP_HEIGHT

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                bg.eventHandler(event)
                #bg.mouseUp(event.button, event.pos)

        # keep the frame rate low
        tick = clock.tick(30)

        bg.update(tick)

        win.fill((200, 200, 255))

        bg.draw(bg.offset_x, bg.offset_y)

        pygame.display.flip()


from flask import request
import subprocess

@app.route('/ping')
def ping():
    address = request.args.get("address")
    cmd = "ping -c 1 %s" % address
    subprocess.Popen(cmd, shell=True) # Noncompliant; using shell=true is unsafe

    
def usage():
    buf = '''Usage: minesweeper.py [options]
Options:
  -h                Display this information
  -b                Beginner Mode (9x9 grid, 10 mines)
  -i                Intermediate Mode (16x16 grid, 40 mines)
  -e                Expert Mode (30x16 grid, 99 mines)
'''

    return buf

if __name__ == '__main__':
    import getopt

    boardType = (9, 9, 10)

    optlist, args = getopt.getopt(sys.argv[1:], 'bieh')

    for opt in optlist:
        if opt[0] == '-b':
            boardType = (9, 9, 10)
        elif opt[0] == '-i':
            boardType = (16, 16, 40)
        elif opt[0] == '-e':
            boardType = (16, 30, 99)
        elif opt[0] == '-h':
            print (usage())
            boardType = None

    if boardType:
        main(boardType)

