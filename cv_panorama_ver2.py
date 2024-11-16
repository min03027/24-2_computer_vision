from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QComboBox, QVBoxLayout, QWidget, QHBoxLayout
)
import cv2 as cv
import numpy as np
import winsound
import sys

class Panorama(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('파노라마 영상')
        self.setGeometry(200, 200, 700, 300)

        # 전체 레이아웃
        main_layout = QVBoxLayout()

        # 상단 버튼들
        button_layout = QHBoxLayout()
        collectButton = QPushButton('영상 수집', self)
        self.showButton = QPushButton('영상 보기', self)
        self.stitchButton = QPushButton('봉합', self)
        self.saveButton = QPushButton('저장하기', self)
        quitButton = QPushButton('나가기', self)

        button_layout.addWidget(collectButton)
        button_layout.addWidget(self.showButton)
        button_layout.addWidget(self.stitchButton)
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(quitButton)

        # 하단 텍스트 라벨
        self.label = QLabel('환영합니다!', self)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.label)

        # 저장 옵션 선택하는 QComboBox (숨겨둡니다)
        self.pickCombo = QComboBox(self)
        self.pickCombo.addItems(['봉합 전 이미지', '봉합 후 이미지'])
        self.pickCombo.setVisible(False)  # 처음에는 보이지 않도록 설정

        # 저장 옵션 ComboBox를 레이아웃에 추가
        main_layout.addWidget(self.pickCombo)

        # 레이아웃 설정
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 버튼 상태 설정
        self.showButton.setEnabled(False)
        self.stitchButton.setEnabled(False)
        self.saveButton.setEnabled(False)

        # 버튼 클릭 연결
        collectButton.clicked.connect(self.collectFunction)
        self.showButton.clicked.connect(self.showFunction)
        self.stitchButton.clicked.connect(self.stitchFunction)
        self.saveButton.clicked.connect(self.showSaveOptions)
        quitButton.clicked.connect(self.quitFunction)

    def collectFunction(self):
        self.showButton.setEnabled(False)
        self.stitchButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.label.setText('c를 여러 번 눌러 수집하고 끝나면 q를 눌러 비디오를 끕니다.')

        self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        if not self.cap.isOpened():
            sys.exit('카메라 연결 실패')

        self.imgs = []
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            cv.imshow('video display', frame)

            key = cv.waitKey(1)
            if key == ord('c'):
                self.imgs.append(frame)
            elif key == ord('q'):
                self.cap.release()
                cv.destroyWindow('video display')
                break

        if len(self.imgs) >= 2:
            self.showButton.setEnabled(True)
            self.stitchButton.setEnabled(True)
            self.saveButton.setEnabled(True)

    def showFunction(self):
        self.label.setText('수집된 영상은 ' + str(len(self.imgs)) + '장 입니다.')
        stack = cv.resize(self.imgs[0], dsize=(0, 0), fx=0.25, fy=0.25)
        for i in range(1, len(self.imgs)):
            stack = np.hstack((stack, cv.resize(self.imgs[i], dsize=(0, 0), fx=0.25, fy=0.25)))
        cv.imshow('Image collection', stack)

    def stitchFunction(self):
        stitcher = cv.Stitcher_create()
        status, self.img_stitched = stitcher.stitch(self.imgs)
        if status == cv.Stitcher_OK:
            cv.imshow('Image stitched panorama', self.img_stitched)
            self.stitched_image_available = True  # 봉합 후 이미지가 준비되었음을 표시
        else:
            winsound.Beep(3000, 500)
            self.label.setText('파노라마 제작에 실패했습니다. 다시 시도하세요.')
            self.stitched_image_available = False  # 실패 시 False

    def showSaveOptions(self):
        # 저장 옵션 콤보박스를 표시합니다.
        if hasattr(self, 'img_stitched') and self.img_stitched is not None:
            self.pickCombo.setVisible(True)  # 봉합 후 이미지가 있으면 콤보박스 표시
        else:
            self.pickCombo.setVisible(True)  # 봉합 전 이미지 저장만 가능하므로

        # 저장하기 버튼이 눌리면 저장 선택 후 이미지 저장
        self.saveButton.clicked.connect(self.saveFunction)

    def saveFunction(self):
        # 파일 저장 대화 상자 열기
        dialog = QFileDialog(self)
        fname, _ = dialog.getSaveFileName(self, '파일 저장', './', 'Images (*.png *.jpg *.bmp)')
        
        if fname:
            # 선택된 콤보박스 항목에 따라 저장
            if self.pickCombo.currentIndex() == 0:  # 봉합 전 이미지 저장
                if hasattr(self, 'imgs') and self.imgs:
                    first_img = self.imgs[0]  # 첫 번째 이미지를 저장
                    cv.imwrite(fname, first_img)
                    self.label.setText(f"봉합 전 이미지가 {fname}에 저장되었습니다.")
                else:
                    self.label.setText("봉합 전 이미지가 없습니다.")
            elif self.pickCombo.currentIndex() == 1:  # 봉합 후 이미지 저장
                if hasattr(self, 'img_stitched') and self.img_stitched is not None:
                    cv.imwrite(fname, self.img_stitched)
                    self.label.setText(f"봉합 후 이미지가 {fname}에 저장되었습니다.")
                else:
                    self.label.setText("봉합 후 이미지가 없습니다. 봉합을 먼저 수행하세요.")
        else:
            self.label.setText("저장 경로가 선택되지 않았습니다.")

    def quitFunction(self):
        self.cap.release()
        cv.destroyAllWindows()
        self.close()

app = QApplication(sys.argv)
win = Panorama()
win.show()
app.exec()
