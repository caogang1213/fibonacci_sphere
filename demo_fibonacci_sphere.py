#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math, random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar

class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.pointquantityspinbox = QSpinBox()
        self.pointquantityspinbox.setEnabled(True)
        self.pointquantityspinbox.setRange(3, 100)
        self.pointquantityspinbox.setSingleStep(1)
        self.pointquantityspinbox.setValue(5)
        self.pointquantityspinbox.valueChanged.connect(self.render_canvas)
        
        self.infotext = QPlainTextEdit()
        self.infotext.setReadOnly(True)

        infolayout = QVBoxLayout()
        infolayout.addWidget(self.pointquantityspinbox)
        infolayout.addWidget(self.infotext)

        infotextContainer = QWidget()
        infotextContainer.setLayout(infolayout)

        displaylayout = QHBoxLayout()
        displaylayout.addWidget(self.canvas)

        displayContainer = QWidget()
        displayContainer.setLayout(displaylayout)

        self.DisplayDock = QDockWidget(u'', self)
        self.DisplayDock.setObjectName(u'')
        self.DisplayDock.setWidget(displayContainer)

        self.setCentralWidget(infotextContainer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.DisplayDock)

        self.dockFeatures = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable
        self.DisplayDock.setFeatures(self.DisplayDock.features() ^ self.dockFeatures)

        self.render_canvas()

    def render_canvas(self):

        from itertools import product, combinations

        self.figure.clear()

        ax = self.figure.gca(projection='3d')
        r = [-1, 1]

        # draw box
        for s, e in combinations(np.array(list(product(r, r, r))), 2):
            if np.sum(np.abs(s-e)) == r[1]-r[0]:
                ax.plot3D(*zip(s, e), color="0")

        # draw sphere
        u, v = np.mgrid[0:2*np.pi:60j, 0:np.pi:40j]
        x = np.cos(u)*np.sin(v)
        y = np.sin(u)*np.sin(v)
        z = np.cos(v)
        ax.plot_wireframe(x, y, z, color="0.75", alpha=0.2)

        points = self.fibonacci_sphere()
        points = np.asarray(points)
        
        # draw origin
        ax.plot([0],[0],[0], 'ro', label ='fruit')

        # draw obtained equally distributed points around the sphere
        ax.plot(points[:,0], points[:,1], points[:,2], 'k^', label ='cameras')

        self.infotext.clear()
        self.infotext.appendPlainText('-----Fabonacci Sphere Algorithm-----\n')
        self.infotext.appendPlainText('Number of Points = %i' % self.pointquantityspinbox.value())

        count = 1
        for point in points:
            self.infotext.appendPlainText('Point %i: %s' % (count, point))
            count+=1

        self.infotext.appendPlainText('---------------')
        combinations = [list(item) for item in combinations(range(self.pointquantityspinbox.value()), 2)]
        for item in combinations:
            i = item[0]
            j = item[1]
            self.infotext.appendPlainText('angle=%.3f, radian=%.3f' % (180*angle(points[i], points[j])/np.pi, radians_(points[i], points[j])))

        self.infotext.appendPlainText('---------------')
        for item in combinations:
            i = item[0]
            j = item[1]
            self.infotext.appendPlainText('Point %i to Point %i: dist=%.4f' % (i, j, dist_3d(points[i], points[j])))
            point = np.vstack((points[i], points[j]))
            # ax.plot(point[:,0], point[:,1], point[:,2], 'c--', alpha=0.3)

        self.infotext.appendPlainText('------------------')
        zeros = np.array([0,0,0])
        count = 1
        for point in points:
            self.infotext.appendPlainText('Point %i to zero: dist=%.4f' % (count, dist_3d(point, zeros)))
            point = np.vstack((zeros, point))
            ax.plot(point[:,0], point[:,1], point[:,2], 'b:')
            count+=1

        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_zlim(-1, 1)
        # plt.axis('off')
        plt.legend()

        # refresh canvas
        self.canvas.draw()

    def fibonacci_sphere(self, randomize=False):
        rnd = 1.
        samples = self.pointquantityspinbox.value()
        if randomize:
            rnd = random.random() * samples

        points = []
        offset = 2./samples
        increment = math.pi * (3. - math.sqrt(5.))

        for i in range(samples):
            y = ((i * offset) - 1) + (offset / 2)
            r = math.sqrt(1 - pow(y,2))

            phi = ((i + rnd) % samples) * increment

            x = math.cos(phi) * r
            z = math.sin(phi) * r

            points.append([x,y,z])

        return points

def dist_3d(point1, point2):
    return np.sqrt((point2[2]-point1[2])**2 + (point2[1]-point1[1])**2 + (point2[0]-point1[0])**2)

def angle(v1, v2): 
    return np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1) * np.linalg.norm(v2)))

def radians_(v1,v2,r=1):
    return r*angle(v1, v2)

def get_main_app(argv=[]):
    app = QApplication(argv)
    win = MainWindow()
    win.show()
    return app, win

def main():
    app, _win = get_main_app(sys.argv)
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())