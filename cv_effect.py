from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QInputDialog
from PyQt6.QtGui import QImage, QPixmap
import cv2 as cv
import numpy as np
import sys


class SpecialEffectApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('특수 효과 및 이미지 합성')
        self.setGeometry(100, 100, 1200, 600)

        # QLabel for previews
        self.previewLabel1 = QLabel(self)
        self.previewLabel1.setGeometry(10, 10, 580, 260)
        self.previewLabel1.setScaledContents(True)

        self.previewLabel2 = QLabel(self)
        self.previewLabel2.setGeometry(600, 10, 580, 260)
        self.previewLabel2.setScaledContents(True)

        self.previewLabelMerged = QLabel(self)
        self.previewLabelMerged.setGeometry(10, 280, 1170, 260)
        self.previewLabelMerged.setScaledContents(True)

        # 버튼들
        pictureButton1 = QPushButton('사진 1 읽기', self)
        pictureButton1.setGeometry(10, 550, 120, 30)
        pictureButton1.clicked.connect(self.loadImage1)

        pictureButton2 = QPushButton('사진 2 읽기', self)
        pictureButton2.setGeometry(140, 550, 120, 30)
        pictureButton2.clicked.connect(self.loadImage2)

        embossButton1 = QPushButton('엠보싱 (사진 1)', self)
        embossButton1.setGeometry(270, 550, 120, 30)
        embossButton1.clicked.connect(lambda: self.applyEffect('emboss', 1))

        cartoonButton1 = QPushButton('카툰 (사진 1)', self)
        cartoonButton1.setGeometry(400, 550, 120, 30)
        cartoonButton1.clicked.connect(lambda: self.applyEffect('cartoon', 1))

        sketchButton1 = QPushButton('연필 스케치 (사진 1)', self)
        sketchButton1.setGeometry(530, 550, 120, 30)
        sketchButton1.clicked.connect(lambda: self.applyEffect('sketch', 1))

        oilButton1 = QPushButton('유화 (사진 1)', self)
        oilButton1.setGeometry(660, 550, 120, 30)
        oilButton1.clicked.connect(lambda: self.applyEffect('oil', 1))

        embossButton2 = QPushButton('엠보싱 (사진 2)', self)
        embossButton2.setGeometry(10, 590, 120, 30)
        embossButton2.clicked.connect(lambda: self.applyEffect('emboss', 2))

        cartoonButton2 = QPushButton('카툰 (사진 2)', self)
        cartoonButton2.setGeometry(140, 590, 120, 30)
        cartoonButton2.clicked.connect(lambda: self.applyEffect('cartoon', 2))

        sketchButton2 = QPushButton('연필 스케치 (사진 2)', self)
        sketchButton2.setGeometry(270, 590, 120, 30)
        sketchButton2.clicked.connect(lambda: self.applyEffect('sketch', 2))

        oilButton2 = QPushButton('유화 (사진 2)', self)
        oilButton2.setGeometry(400, 590, 120, 30)
        oilButton2.clicked.connect(lambda: self.applyEffect('oil', 2))

        mergeButton = QPushButton('합성', self)
        mergeButton.setGeometry(530, 590, 120, 30)
        mergeButton.clicked.connect(self.mergeImages)

        subtitleButton = QPushButton('자막 추가', self)
        subtitleButton.setGeometry(660, 590, 120, 30)
        subtitleButton.clicked.connect(self.addSubtitle)

        saveButton = QPushButton('저장하기', self)
        saveButton.setGeometry(790, 590, 120, 30)
        saveButton.clicked.connect(self.saveMergedImage)

        quitButton = QPushButton('나가기', self)
        quitButton.setGeometry(920, 590, 120, 30)
        quitButton.clicked.connect(self.close)

    def loadImage1(self):
        fname, _ = QFileDialog.getOpenFileName(self, '사진 1 읽기', './', "Image files (*.jpg *.png)")
        if fname:
            self.img1 = cv.imread(fname)
            self.updatePreview(self.img1, self.previewLabel1)

    def loadImage2(self):
        fname, _ = QFileDialog.getOpenFileName(self, '사진 2 읽기', './', "Image files (*.jpg *.png)")
        if fname:
            self.img2 = cv.imread(fname)
            self.updatePreview(self.img2, self.previewLabel2)

    def applyEffect(self, effect, img_index):
        if img_index == 1 and hasattr(self, 'img1'):
            self.img1 = self.processEffect(self.img1, effect)
            self.updatePreview(self.img1, self.previewLabel1)
        elif img_index == 2 and hasattr(self, 'img2'):
            self.img2 = self.processEffect(self.img2, effect)
            self.updatePreview(self.img2, self.previewLabel2)

    def processEffect(self, img, effect):
        if effect == 'emboss':
            kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
            return cv.filter2D(img, -1, kernel)
        elif effect == 'cartoon':
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            edges = cv.adaptiveThreshold(cv.medianBlur(gray, 7), 255, cv.ADAPTIVE_THRESH_MEAN_C,
                                         cv.THRESH_BINARY, 9, 2)
            color = cv.bilateralFilter(img, 9, 75, 75)
            return cv.bitwise_and(color, color, mask=edges)
        elif effect == 'sketch':
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            inv = cv.bitwise_not(gray)
            blur = cv.GaussianBlur(inv, (21, 21), 0)
            sketch = cv.divide(gray, 255 - blur, scale=256)
            return cv.cvtColor(sketch, cv.COLOR_GRAY2BGR)
        elif effect == 'oil':
            return cv.xphoto.oilPainting(img, 7, 1)

    def mergeImages(self):
        if hasattr(self, 'img1') and hasattr(self, 'img2'):
            height1, width1 = self.img1.shape[:2]
            height2, width2 = self.img2.shape[:2]
            max_height = max(height1, height2)
            total_width = width1 + width2
            merged_img = np.zeros((max_height, total_width, 3), dtype=np.uint8)
            merged_img[:height1, :width1] = self.img1
            merged_img[:height2, width1:] = self.img2
            self.merged_img = merged_img
            self.updatePreview(merged_img, self.previewLabelMerged)

    def addSubtitle(self):
        if hasattr(self, 'merged_img'):
            text, ok = QInputDialog.getText(self, '자막 입력', '영어로 자막을 입력하세요:')
            if ok and text:
                img_with_subtitle = self.merged_img.copy()
                font = cv.FONT_HERSHEY_SIMPLEX
                font_scale = 1.0
                font_thickness = 2
                color = (255, 255, 255)  # White
                bg_color = (0, 0, 0)  # Black background for text
                text_size = cv.getTextSize(text, font, font_scale, font_thickness)[0]
                text_x = (img_with_subtitle.shape[1] - text_size[0]) // 2
                text_y = img_with_subtitle.shape[0] - 20

                # Draw background rectangle
                cv.rectangle(img_with_subtitle,
                             (text_x - 10, text_y - text_size[1] - 10),
                             (text_x + text_size[0] + 10, text_y + 10),
                             bg_color, -1)

                # Draw text
                cv.putText(img_with_subtitle, text, (text_x, text_y), font, font_scale, color, font_thickness)

                self.merged_img = img_with_subtitle
                self.updatePreview(self.merged_img, self.previewLabelMerged)

    def saveMergedImage(self):
        if hasattr(self, 'merged_img'):
            fname, _ = QFileDialog.getSaveFileName(self, '저장하기', './merged.jpg', "Image files (*.jpg *.png)")
            if fname:
                cv.imwrite(fname, self.merged_img)

    def updatePreview(self, img, label):
        rgb_image = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = SpecialEffectApp()
    mainWindow.show()
    sys.exit(app.exec())
