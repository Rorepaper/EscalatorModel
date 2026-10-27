from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QAction, QPainter, QColor, QPainterPath, QPen, QFont
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QMainWindow, QLCDNumber
from PyQt6.QtWidgets import QMenu
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog
from ParamsDialog import ParamsDialog
from Escalator import EscalatorModel
from PyQt6.QtWidgets import QMessageBox
from Human import Human
from random import randint


class ModelWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.esc_model = EscalatorModel()
        self.stairs_x = list(range(130, 960, 30))
        self.startTimer(16)
        self.speed = 1
        self.humans = []
        self.esc_model.v = self.speed * 0.75
        self.params_dialog = ParamsDialog()
        self.lam = 2500
        self.P_walk = 0.4
        self.params_dialog.accepted.connect(self.slot_params_accepted)
        self.setFixedSize(1400, 900)
        self.setWindowTitle('Escalator Model')
        self.digits = [QLCDNumber(self) for _ in range(3)]
        for i in range(len(self.digits)):
            self.digits[i].setFixedSize(150, 40)
            self.digits[i].move(300, 200 + 50 * i)
            self.digits[i].display(100)
            self.digits[i].setStyleSheet('''QLCDNumber {color: red;
        background-color: black;}''')
        menu_bar = self.menuBar()

        menu1 = QMenu('File', self)
        self.save_txt_action = QAction('Save as .txt', self)
        self.save_pdf_action = QAction('Save as .png', self)
        menu1.addAction(self.save_txt_action)
        menu1.addAction(self.save_pdf_action)

        self.save_txt_action.triggered.connect(self.slot_save_txt)
        self.save_pdf_action.triggered.connect(self.slot_save_png)

        menu2 = QMenu('Settings', self)
        self.set_params_action = QAction('Set Params', self)
        self.set_default_action = QAction('Set Default', self)
        menu2.addAction(self.set_params_action)
        menu2.addAction(self.set_default_action)

        self.set_params_action.triggered.connect(self.slot_open_params)
        self.set_default_action.triggered.connect(self.slot_set_default)

        menu3 = QMenu('Info', self)
        self.about_action = QAction('About', self)
        self.exit_action = QAction('Exit', self)
        menu3.addAction(self.about_action)
        menu3.addAction(self.exit_action)

        self.about_action.triggered.connect(self.slot_about)
        self.exit_action.triggered.connect(self.close)

        menu_bar.addMenu(menu1)
        menu_bar.addMenu(menu2)
        menu_bar.addMenu(menu3)
        self.set_params()

    def timerEvent(self, a0):
        for i in range(len(self.stairs_x)):
            if self.stairs_x[i] + self.speed > 900:
                self.stairs_x[i] = 130
            else:
                self.stairs_x[i] += self.speed
        self.update()
        for human in self.humans:
            human.look()
            human.move()

    def paintEvent(self, a0):
        painter = QPainter(self)
        self.paint_model(painter)

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()
        elif a0.key() == Qt.Key.Key_Space:
            print(self.speed)
            self.set_speed(self.speed % 3 + 1)

    def mousePressEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton:
            self.humans.append(Human(a0.pos().x(), -100, self.speed, False))
            self.lam += 100
        elif a0.button() == Qt.MouseButton.MiddleButton:
            self.humans.append(Human(a0.pos().x(), -100, self.speed, True))
            self.lam += 100
        else:
            for human in self.humans:
                if abs(human.x - a0.pos().x()) < 40:
                    self.humans.remove(human)
                    self.lam -= 100
                    break
        walking_count = sum(1 for h in self.humans if h.is_going)
        if len(self.humans) > 0:
            self.P_walk = walking_count / len(self.humans)
        else:
            self.P_walk = 0
        res = self.esc_model.simulate(self.lam, self.P_walk)
        print(res)
        self.digits[0].display(res['real_capacity'])
        self.digits[1].display(res['total_load_kg'])
        self.digits[2].display(res['current_queue'])
        self.update()

    def paint_model(self, painter: QPainter):
        painter.begin(self)
        painter.setBrush(QColor(160, 197, 205))
        painter.setPen(QColor(155, 188, 197))
        painter.fillRect(0, 0, 1400, 900, painter.brush())
        for i in range(50, 1400, 50):
            painter.drawLine(i, 0, i, 900)
        for j in range(50, 900, 50):
            painter.drawLine(0, j, 1400, j)
        painter.fillRect(0, 0, 1400, 100, QColor(144, 131, 122))
        path = QPainterPath()
        path.moveTo(0, 900)
        path.lineTo(1400, 900)
        path.lineTo(1400, 380)
        path.lineTo(1000, 380)
        path.lineTo(1000, 800)
        path.lineTo(0, 800)
        painter.fillPath(path, QColor(144, 131, 122))
        painter.setPen(QPen(QColor(0, 0, 0), 4))
        painter.setBrush(QColor(99, 99, 109))
        for stair in self.stairs_x:
            painter.drawPie(stair, int(350 + (900 - stair) * 0.53), 60, 40,
                            16 * 180, 16 * 60)
        for human in self.humans:
            human.draw(painter)
        painter.fillPath(escalator_path(400, 20), QColor(99, 99, 109))
        painter.fillPath(escalator_path(325, 10), QColor(99, 99, 109))
        painter.fillPath(escalator_path(380, 55), QColor(177, 244, 255, 100))
        painter.fillRect(900, 325, 35, 55, QColor(99, 99, 109))
        painter.fillRect(115, 725, 35, 55, QColor(99, 99, 109))
        painter.fillRect(975, 300, 25, 500, QColor(206, 203, 210))
        QSvgRenderer('screen.svg').render(painter, QRectF(125, 115, 350, 250))
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.setFont(QFont('Consolas', 16))
        painter.drawText(140, 210, 350, 250, Qt.AlignmentFlag.AlignLeft,
                         'REAL CAPACITY')
        painter.drawText(140, 260, 350, 250, Qt.AlignmentFlag.AlignLeft,
                         'TOTAL LOAD')
        painter.drawText(140, 310, 350, 250, Qt.AlignmentFlag.AlignLeft,
                         'CURRENT QUEUE')

    def slot_params_accepted(self, params):
        self.lam = params['lam']
        self.P_walk = params['P_walk']
        self.set_params()
        self.update()

    def set_params(self):
        self.humans = [Human(randint(0, 1400), 0, self.speed, False) for _ in
                       range(int(self.lam / 100 * (1 - self.P_walk)))]
        self.humans += [Human(randint(0, 1400), 0, self.speed, True) for _ in
                        range(int(self.lam / 100 * self.P_walk))]
        res = self.esc_model.simulate(self.lam, self.P_walk)
        self.digits[0].display(res['real_capacity'])
        self.digits[1].display(res['total_load_kg'])
        self.digits[2].display(res['current_queue'])

    def set_speed(self, speed):
        self.speed = speed
        self.esc_model.v = self.speed * 0.75
        for human in self.humans:
            human.speed = self.speed
        self.update()

    def slot_open_params(self):
        self.params_dialog.show()

    def slot_save_txt(self):
        res = self.esc_model.simulate(self.lam, self.P_walk)

        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить как TXT',
            f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            'Text files (*.txt)'
        )

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(
                    f'''
Отчет по моделированию эскалатора
Дата: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
{"=" * 50}
Интенсивность потока: {self.lam} чел/час
Доля идущих: {self.P_walk}
Эффективная доля идущих: {res["eff_p_walk"]}
Пропускная способность: {res["real_capacity"]} чел/час
Нагрузка: {res["total_load_kg"]} кг ({res["load_percent"]}%)
Очередь: {res["current_queue"]} чел
Мощность: {res["power_kw"]} кВт
Перегрузка: {"ДА" if res["overload"] else "НЕТ"}
                '''
                )
            QMessageBox.information(self, 'Сохранение',
                                    f'Сохранено: {file_path}')

    def slot_save_png(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить как PNG',
            f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
            'PNG files (*.png)'
        )

        if not file_path:
            return

        pixmap = self.grab()
        pixmap.save(file_path)

        QMessageBox.information(self, 'Сохранение',
                                f'Скриншот сохранен: {file_path}')

    def slot_set_default(self):
        self.lam = 2500
        self.P_walk = 0.2
        self.set_params()
        self.set_speed(1)
        print('Сброс к стандарту')

    def slot_about(self):
        QMessageBox.about(
            self,
            'About',
            '''
              <h3>Escalator Model</h3>
              <p>Model for calculating throughput and<br>
              brake system load of an escalator.</p>
              <p>Based on RD 10-172-97</p>
              <p>Version 1.0</p>
              '''
        )


def escalator_path(y, h):
    path = QPainterPath()
    path.moveTo(975, y)
    path.lineTo(900, y)
    path.lineTo(150, y + 400)
    path.lineTo(75, y + 400)
    path.lineTo(75, y + 400 - h)
    path.lineTo(150, y + 400 - h)
    path.lineTo(900, y - h)
    path.lineTo(975, y - h)
    return path