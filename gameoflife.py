import numpy as np 
import argparse
from matplotlib import cm
import random
from PIL import Image
import PIL.ImageOps
import datetime as dt
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from enum import Enum
class Neighbours(object):
    VON_NEUMANN = [(0,1),(0,-1),(1,0),(-1,0)]

    MOORE = [(-1,-1),(-1,0),(1,0),(1,1),
                   (0,1),(0,-1),(-1,1),(1,-1)]

class GameOfLife(object):

    def __init__(self,size=10,neighbours=Neighbours.MOORE):
        self.board = np.zeros((size,size),dtype=int)
        self.size = size 
        self.iteration = 0
        self.neighbours = neighbours 
    
    def image_to_np_arr(self,img_path):
        # load the image 
        img = Image.open(img_path).convert('1')
        img_resized = img.resize((self.size,self.size))
        img_arr_rs = np.asarray(img_resized, dtype="int")
        img_inv = self.invert(deepcopy(img_arr_rs))
        b,w = self.pcent_bw(img_arr_rs)
        if w < b:
            img = img_inv
        else:
            img = img_arr_rs
         
        return img 
    
    def invert(self,img):
        for i in range(self.size):
            for j in range(self.size):
                if img[i][j] == 1:
                    img[i][j] = 0
                else:
                    img[i][j] = 1
        return img
    def pcent_bw(self,img):
        num_w = 0
        num_b = 0
        for i in range(self.size):
            for j in range(self.size):
                if img[i][j] == 1:
                    num_w += 1
                else:
                    num_b += 1
        return num_w,num_b

    def process_img(self,img_path):
        data = self.image_to_np_arr(img_path)
        self.board = data

    def init_population(self,init_alive):
        cells = set()

        while len(cells) < init_alive: 
            # generate random x,y
            pt = (random.randint(1,self.size),
                  random.randint(1,self.size))

            cells.add(pt)

        for (x,y) in cells: 
            self.board[self.size-y][self.size-x] = 1
        print("LEN CELLS: ", len(cells))
    def iterate(self):

        alive_cells = []
        dead_cells = []
        
        for row in range(self.size):
            for col in range(self.size):
                cell = self.board[row][col]
                
                alive_nb,dead_nb = self.classify_neighbours(row,col)
                # if the cell is alive 
                if cell == 1:

                    # loneliness 
                    if alive_nb < 2:
                        dead_cells.append((row,col))
                    # overcrowding
                    elif alive_nb > 3:
                        dead_cells.append((row,col))
                    elif alive_nb == 2 or alive_nb == 3:
                        alive_cells.append((row,col))
                else:
                    if alive_nb == 3:
                        alive_cells.append((row,col))

        self.update_board(alive_cells,dead_cells)
        return deepcopy(self.board)

    def update_board(self,alive_cells,dead_cells):
        for r,c in alive_cells:
            self.board[r][c] = 1

        for r,c in dead_cells:
            self.board[r][c] = 0

    def classify_neighbours(self,row,col):
        num_dead = 0 
        num_alive = 0
        for (r_offset,c_offset) in self.neighbours:
            new_r = row + r_offset
            new_c = col + c_offset
            
            # assume a toroidal board --> wrap around of coordinates 

            if self.board[new_r%self.size][new_c%self.size] == 0:
                num_dead += 1
            else:
                num_alive += 1
        return (num_alive,num_dead)

    def get_frames(self,num_itr):
        frames = []
        for i in range(10):
            frames.append(deepcopy(self.board))
        for i in range(num_itr):
            frames.append(self.iterate())

        return frames
    
    def animate(self,num_itr=100):
        fig = plt.figure(figsize=(5, 5), dpi=250)
        fig.set_facecolor((156/255,205/255,151/255))
        plt.axis('off')
        figures = self.get_frames(num_itr)
        ims = []
        for i in range(len(figures)):
            im = plt.imshow(figures[i],cmap=plt.get_cmap('Accent'),animated=True, interpolation='nearest')
            text_str = "Generation: {:4d}".format(i)
            ims.append([im])
        return fig, ims
    def __str__(self):
        output = ''

        for i in range(self.size):
            for j in range(self.size):
                output += str(self.board[i][j]) + ' '    
            output += '\n'
        return output
    


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Conways Game of Life')
    parser.add_argument('-p', '--pcent',
                            help='Percentage Alive',
                            choices=range(1,101),
                            default=25,
                            type=int)
    
    parser.add_argument('-s', '--size',
                            help='Simulation Size',
                            default=80,
                            type=int)

    parser.add_argument('-n', '--neighbours',
                            help='Neighbour Type',
                            choices={"vn", "moore"},
                            default="moore",
                            type=str)

    parser.add_argument('-g', '--generations',
                            help='Generations of Simulation',
                            default=100,
                            type=int)
    parser.add_argument('-i', '--image',
                            help='Image Location',
                            default=None,
                            type=str)
    args = parser.parse_args()

    if args.neighbours == "vn":
        nb = Neighbours.VON_NEUMANN
    else:
        nb = Neighbours.MOORE

    pcent = args.pcent 
    size = args.size
    iterations = args.generations
    game = GameOfLife(size,neighbours=nb)
    if args.image is not None: 
        game.process_img(args.image)
    else: 
        game.init_population(int(size*size*pcent*0.01))
    #plt.imshow(game.board, interpolation='nearest')
    #plt.show()

    fig, ims = game.animate(iterations)
    ani = animation.ArtistAnimation(fig, ims, interval=30, blit=True, repeat_delay=1000)
    ani.save('gol_prop{}_s{}_itr{}_time_{}.mp4'.format(pcent,
                                                       size,
                                                       iterations,
                                                       dt.datetime.now().time()))
    plt.show()
