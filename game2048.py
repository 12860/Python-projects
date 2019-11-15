
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
2048game
"""
#deal user input
from random import randrange,choice
from collections import defaultdict
import curses

letter_codes=[ord(ch) for ch in 'WASDRQwasdrq']
actions=['up','left','down','right','restart','exit']
actions_dict=dict(zip(letter_codes,actions * 2))

def get_user_action(keyboard):
    char="N"
    while char not in actions_dict:
        char=keyboard.getch()
    return actions_dict[char]

def transpose(field):
    return [list(row) for row in zip(*field)]

def invert(field):
    return [row[::-1] for row in field]
    
class GameField(object):
    def __init__(self,height=4,width=4,win=2048):
        self.height=height
        self.width=width
        self.win_value=win
        self.score=0
        self.highscore=0
        self.reset()
    
    def reset(self):
        if self.score > self.highscore:
            self.highscore=self.score
        self.score=0
        #self.field is 4*4 matrix,0,1,2,3
        self.field=[[0 for i in range(self.width)] for j in range(self.height)]
        #generate 2 or 4
        self.spawn()
        self.spawn()
  
    def spawn(self):
        new_element= 4 if randrange(100)>89 else 2
        (i,j)=choice([(i,j) for i in range(self.height) for j in range(self.width) if self.field[i][j]==0])
        self.field[i][j]=new_element
    
    def move(self,direction):
        def move_row_left(row):
            def tighten(row):
                new_row=[i for i in row if i!=0]
                new_row+=[0 for i in range(len(row)-len(new_row))]          
                return new_row
                
            def merge(row):
                new_row=[]
                pair=False
                for i in range(len(row)):
                    if pair:
                        self.score+=row[i]*2
                        new_row.append(2*row[i])
                        pair=False
                    else:
                        if i+1<len(row) and row[i]==row[i+1]:
                            pair=True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row)==len(row)
                return new_row
            return tighten(merge(tighten(row)))
        
        moves={}
        moves['left']=lambda field:[move_row_left(row) for row in field]
        moves['right']=lambda field:invert(moves['left'](invert(field)))
        moves['up']=lambda field:transpose(moves['left'](transpose(field)))
        moves['down']=lambda field:transpose(moves['right'](transpose(field)))
        
        if direction in moves:
            if self.move_is_possible(direction):
                self.field=moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False
        
    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)
            
    def is_win(self):
        return any(any(i >= self.win_value for i in row)for row in self.field)
    
    def move_is_possible(self,direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i]==0 and row[i+1]!=0 :
                    return True
                if row[i]!=0 and row[i+1]==row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row)-1))
        check={}
        check['left']=lambda field: any(row_is_left_movable(row) for row in field)
        check['right']=lambda field: check['left'](invert(field))
        check['up']=lambda field : check['left'](transpose(field))
        check['down']=lambda field: check['right'](transpose(field))
        
        if direction in check:
            return check[direction](self.field)
        else:
            return False
    
    def draw(self,screen):
        help_string1='(W)up (S)down (A)left (D)right'
        help_string2='      (R)restart  (Q)exit'
        gameover_string='           GAME OVER'
        win_string='        YOU WIN!'
        def cast(string):
            screen.addstr(string+'\n')
    
        def draw_hor_separator():
            line='+'+('+------'*self.width+'+')[1:]
            separator=defaultdict(lambda:line)
            if not hasattr(draw_hor_separator,"counter"):
                draw_hor_separator.counter=0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter+=1
        
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num>0 else'|      ' for num in row)+
            '|')
        
        screen.clear()
        cast('SCORE: '+str(self.score))
        if 0!=self.highscore:
            cast('HIGHSCORE '+str(self.highscore))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)


def main(stdscr):
    def init():
        game_field.reset()
        return 'game'
    
    def not_game(state):
        game_field.draw(stdscr)
        
        action=get_user_action(stdscr)
        responses=defaultdict(lambda:state)
        responses['restart'],responses['exit']='init','exit'
        return responses[action]
    
    def game():
        game_field.draw(stdscr)
        
        action=get_user_action(stdscr)
        
        if action=='restart':
            return 'init'
        if action=='exit':
            return 'exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'win'
            if game_field.is_gameover():
                return 'gameover'
        return 'game'
    
    state_actions={
            'init':init,
            'win':lambda:not_game('win'),
            'gameover':lambda:not_game('gameover'),
            'game':game
        }
    
    curses.use_default_colors()
    
    game_field=GameField(win=32)
    
    state='init'
    
    while state != 'exit':
        state=state_actions[state]()

curses.wrapper(main)
    
    
    
        
            
            
