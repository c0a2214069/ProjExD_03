import random
import sys
import time
import math
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数
NUM_OF_BEAMS = 5 #ビームの数

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"),0,2.0)#左向き
        img1 = pg.transform.flip(img0,True,False)#右向き
        self.images = {(+5,0):img1,(-5,0):img0,(+5,-5):pg.transform.rotozoom(img1,45,1.0),(0,-5):pg.transform.rotozoom(img1,90,1.0),(+5,+5):pg.transform.rotozoom(img1,-45,1.0),(0,+5):pg.transform.rotozoom(img1,-90,1.0),(-5,+5):pg.transform.rotozoom(img0,45,1.0),(-5,-5):pg.transform.rotozoom(img0,-45,1.0)}
        self.img = self.images[(+5,0)]
        self.rct = self.img.get_rect()
        self.rct.center = xy
        self.dire=(+5,0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if sum_mv != [0,0]:
            self.dire=tuple(sum_mv)
            self.img = self.images[tuple(sum_mv)]
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        引数に基づきビームSurfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        
        self.vx, self.vy = bird.dire[0], bird.dire[1]
        atan = math.atan2(-self.vy,self.vx)
        angle = math.degrees(atan)
        self.img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/beam.png"), angle, 2.0)
        self.rct = self.img.get_rect()
        self.rct.centerx = bird.rct.centerx+bird.rct.width*self.vx/5
        self.rct.centery = bird.rct.centery+bird.rct.height*self.vy/5
        
    
    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    def __init__(self):
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = [0,0,255]
        self.score = 0
        self.img = self.font.render(f"スコア:{self.score}", 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = 100,HEIGHT-50
    def update(self,screen:pg.Surface):
        self.img = self.font.render(f"スコア:{self.score}",0,self.color)
        screen.blit(self.img,self.rct)
    def score_up(self):
        self.score += 1
        



def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    # bomb = Bomb((255, 0, 0), 10)
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []
    beam = None

    clock = pg.time.Clock()
    tmr = 0
    score = Score()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beam = Beam(bird)  # ビームクラスのインスタンスを生成する
                beams.append(beam)
                
        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
        
        for i, bomb in enumerate(bombs):
            for j,beam in enumerate(beams):
                if bomb.rct.colliderect(beam.rct):
                    bombs.pop(i)
                    beams.pop(j)
                    bird.change_img(6, screen)
                    score.score_up()
                    pg.display.update() 

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for bomb in bombs:
            bomb.update(screen)
        if beam is not None:
            beam.update(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()