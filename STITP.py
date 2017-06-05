# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *
import pygame.font
import math
import operator
import time
import sys
from numpy import *
from PIL import Image
from os import listdir

 
pad_width = 800
pad_height = 600
f_name = "Number.png"

num1 = 0
num2 = 0
num3 = 0
checknum = 0



def show_text(surface_handle, pos, text, color, font_bold = False, font_size = 13, font_italic = False):   
    ''''' 
    Function:文字处理函数 
    Input：surface_handle：surface句柄 
           pos：文字显示位置 
           color:文字颜色 
           font_bold:是否加粗 
           font_size:字体大小 
           font_italic:是否斜体 
    Output: NONE 
    '''         
    #获取系统字体，并设置文字大小  
    cur_font = pygame.font.SysFont("microsoftyaheimicrosoftyaheiui", font_size)  
      
    #设置是否加粗属性  
    cur_font.set_bold(font_bold)  
      
    #设置是否斜体属性  
    cur_font.set_italic(font_italic)  
      
    #设置文字内容  
    text_fmt = cur_font.render(text, 1, color,(255,255,255))  
      
    #绘制文字  
    surface_handle.blit(text_fmt, pos)  

def img2vector(filename):
    # 将图片转换为向量
    returnVect = zeros((1,1024))
    # 打开数据文件，读取每行内容
    fr = open(filename)
    for i in range(32):
        # 读取每一行
        lineStr = fr.readline()
        # 将每行前32字符转成int存入向量
        for j in range(32):
            returnVect[0,32*i+j] = int(lineStr[j])
    return returnVect

# 样本数据的类标签列表
hwLabels = []
# 样本数据文件列表
trainingFileList = listdir('digits/trainingDigits')
m = len(trainingFileList)
# 初始化样本数据矩阵（M*1024）
trainingMat = zeros((m,1024))
# 依次读取所有样本数据到数据矩阵
for i in range(m):
    # 提取文件名中的数字
    fileNameStr = trainingFileList[i]
    fileStr = fileNameStr.split('.')[0]
    classNumStr = int(fileStr.split('_')[0])
    hwLabels.append(classNumStr)

    # 将样本数据存入矩阵
    trainingMat[i,:] = img2vector('digits/trainingDigits/%s' % fileNameStr)

def classify0(inX, dataSet, labels, k):
    # inX：用于分类的输入向量,dataSet：输入的训练样本集,labels：样本数据的类标签向量,k：用于选择最近邻居的数目

    # 获取样本数据数量
    dataSetSize = dataSet.shape[0]

    # 矩阵运算，计算测试数据与每个样本数据对应数据项的差值
    diffMat = tile(inX, (dataSetSize,1)) - dataSet

    # sqDistances 上一步骤结果平方和
    sqDiffMat = diffMat**2
    sqDistances = sqDiffMat.sum(axis=1)

    # 取平方根，得到距离向量
    distances = sqDistances**0.5

    # 按照距离从低到高排序
    sortedDistIndicies = distances.argsort()
    classCount={}

    # 依次取出最近的样本数据
    for i in range(k):
        # 记录该样本数据所属的类别
        voteIlabel = labels[sortedDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel,0) + 1

    # 对类别出现的频次进行排序，从高到低
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)

    # 返回出现频次最高的类别
    return sortedClassCount[0][0]

class Brush():
    def __init__(self, screen):
        self.screen = screen
        self.color = (0, 0, 0)
        self.size  = 18
        self.drawing = False
        self.last_pos = None
        self.space = 1
        # if style is True, normal solid brush
        # if style is False, png brush
        self.style = False
        # load brush style png
        self.brush = pygame.image.load("./painter/brush.png").convert_alpha()
        # set the current brush depends on size
        self.brush_now = self.brush.subsurface((0,0), (1, 1))
 
    def start_draw(self, pos):
        self.drawing = True
        self.last_pos = pos
    def end_draw(self):
        self.drawing = False
 
    def set_brush_style(self, style):
        print "* set brush style to", style
        self.style = style
    def get_brush_style(self):
        return self.style
 
    def get_current_brush(self):
        return self.brush_now
 
    def set_size(self, size):
        if size < 0.5: size = 0.5
        elif size > 32: size = 32
        print "* set brush size to", size
        self.size = size
        self.brush_now = self.brush.subsurface((0,0), (size*2, size*2))
    def get_size(self):
        return self.size
 
    def set_color(self, color):
        self.color = color
        for i in xrange(self.brush.get_width()):
            for j in xrange(self.brush.get_height()):
                self.brush.set_at((i, j),
                        color + (self.brush.get_at((i, j)).a,))
    def get_color(self):
        return self.color
 
    def draw(self, pos):
        if self.drawing:
            for p in self._get_points(pos):
                # draw eveypoint between them
                if self.style == False:
                    pygame.draw.circle(self.screen, self.color, p, self.size)
                else:
                    self.screen.blit(self.brush_now, p)
 
            self.last_pos = pos
 
    def _get_points(self, pos):
        """ Get all points between last_point ~ now_point. """
        points = [ (self.last_pos[0], self.last_pos[1]) ]
        len_x = pos[0] - self.last_pos[0]
        len_y = pos[1] - self.last_pos[1]
        length = math.sqrt(len_x ** 2 + len_y ** 2)
        step_x = len_x / length
        step_y = len_y / length
        for i in xrange(int(length)):
            points.append(
                    (points[-1][0] + step_x, points[-1][1] + step_y))
        points = map(lambda x:(int(0.5+x[0]), int(0.5+x[1])), points)
        # return light-weight, uniq integer point list
        return list(set(points))
 
 
class Painter():
    def __init__(self):
        #创建画板
        self.screen = pygame.display.set_mode((pad_width, pad_height))
        pygame.display.set_caption("手写识别智能教学系统")
        self.clock = pygame.time.Clock()
        self.brush = Brush(self.screen)
        pygame.font.init()

    def draw_UI(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (544, 344, 256, 256),1)
        pygame.font.get_fonts()
        font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 50)
        font_surface = font.render(u"手写识别智能教学系统", 1, (0, 0, 0))
        self.screen.blit(font_surface, (150, 0))
        image_ico = pygame.image.load("./painter/panda.png")
        image_ico_small = pygame.transform.scale(image_ico,(64, 64))
        self.screen.blit(image_ico_small, (30, 0))
        self.screen.blit(image_ico_small, (706, 0))

        show_text(self.screen, (120, 140), u"请尝试解答以下题目:", (0, 0, 0), 0,32)
        show_text(self.screen, (120, 220), u"    +      =  __", (0, 0, 0), 0,48)
        show_text(self.screen, (120, 310), u"你的结果是：", (0, 0, 0), 0,32)
        show_text(self.screen, (550, 300), u"手写识别区:", (0, 0, 0), 0,28)

        image_btn_submit = pygame.image.load("./painter/button.png")
        self.screen.blit(image_btn_submit,(300, 515))
        image_btn_clear = pygame.image.load("./painter/button2.png")
        self.screen.blit(image_btn_clear,(300, 430))
        image_btn_fresh = pygame.image.load("./painter/fresh.png")
        self.screen.blit(image_btn_fresh,(600, 160))

    def draw_clear(self):
        pygame.draw.rect(self.screen, (255,255,255), (545, 345, 254, 254))

    def gen_qs(self):
        self.draw_clear()
        global num1
        global num2
        global num3
        global checknum
        num1 = random.randint(0, 9)
        num2 = random.randint(0, 9)
        num3 = num1 + num2

        checknum = num3 %10
        

        
        show_text(self.screen, (360, 230), "    ", (0, 0, 0), 1,36)
        show_text(self.screen, (135, 230), str(num1), (0, 0, 0), 1,36)
        show_text(self.screen, (240, 230), str(num2), (0, 0, 0), 1,36)
        if num3 > 9:
            show_text(self.screen, (360, 230), "1", (0, 0, 0), 1,36)

    def btn_comp(self):
        #显示题目答案
        global checknum
        show_text(self.screen, (380, 230), str(checknum), (0, 0, 0), 1,36)
        Capture = pygame.transform.chop(self.screen, (0, 0, 545, 345))
        pygame.image.save(Capture, f_name)
        vectorUnderTest = timage()
        classifierResult = classify0(vectorUnderTest, trainingMat, hwLabels, 3)
        print ("The Result is %d\n"%classifierResult),
        show_text(self.screen, (380, 305), str(classifierResult), (0, 0, 0), 1,36)

        if classifierResult == checknum:
            image_btn_yes = pygame.image.load("./painter/yes.png")
            self.screen.blit(image_btn_yes,(600, 160))
        else:
            image_btn_no = pygame.image.load("./painter/no.png")
            self.screen.blit(image_btn_no,(600, 160))
 
    def run(self):
        self.screen.fill((255, 255, 255))
        self.draw_UI()
        self.gen_qs()
        while True:
            # max fps limit
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()  
                    sys.exit()
                elif event.type == KEYDOWN:
                    # press esc to clear screen
                    if event.key == K_ESCAPE:
                        self.draw_clear()
                    elif event.key == K_RETURN:
                        Capture = pygame.transform.chop(self.screen, (0, 0, 545, 345))
                        pygame.image.save(Capture, f_name)
                        vectorUnderTest = timage()
                        classifierResult = classify0(vectorUnderTest, trainingMat, hwLabels, 3)
                        print ("The Result is %d"%classifierResult),
                    elif event.key == K_r:
                        self.screen.fill((255, 255, 255))
                        self.draw_UI()
                        
                elif event.type == MOUSEBUTTONDOWN:
                    
                    if ((event.pos)[0] >= 562 and (event.pos)[1] >=362):
                        self.brush.start_draw(event.pos)
                    elif (300 <= (event.pos)[0] <= 527 and 515 <= (event.pos)[1] <= 600):
                        self.btn_comp()
                    elif (300 <= (event.pos)[0] <= 527 and 430 <= (event.pos)[1] <= 514):
                        self.draw_clear()
                    elif (600 <= (event.pos)[0] <= 728 and 160 <= (event.pos)[1] <= 288):
                        self.gen_qs()
                        image_btn_fresh = pygame.image.load("./painter/fresh.png")
                        self.screen.blit(image_btn_fresh,(600, 160))

                        
                    else:
                        pass
                elif event.type == MOUSEMOTION:
                    if ((event.pos)[0] >= 562 and (event.pos)[1] >=362):
                        self.brush.draw(event.pos)
                    else:
                        pass
                elif event.type == MOUSEBUTTONUP:
                    self.brush.end_draw()

            text_time = u"时间:%s" % time.strftime("%H:%M:%S", time.localtime())  
            show_text(self.screen, (20, 570), text_time, (0, 0, 0), True)
            
            pygame.display.update()



def get_char(r,g,b,alpha = 256):
    if g == 255:
        return '0'
    else:
        return '1'

def timage():
    "转换为32*32的图像,原文件名保存"
    im = Image.open(f_name) 
    im_ss = im.resize((32,32))
    im_ss.save(f_name)
    txt = ""
    returnVect = zeros((1,1024))
    for i in range(32):
        for j in range(32):
            returnVect[0,32*i+j] = int(get_char(*im_ss.getpixel((j,i))))
            txt += get_char(*im_ss.getpixel((j,i)))
        txt += '\n' 
    print txt
    return returnVect




if __name__ == '__main__':
    app = Painter()
    app.run()
