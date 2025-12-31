import cv2
import numpy as np

class FaceDetect:
    def __init__(self):
        self._cascade_path = '../data/opencv/haarcascade_frontalface_alt.xml'
        self._naul = '../data/opencv/naul.jpg'

    def rotate_image(self, image, angle):
        """이미지를 주어진 각도로 회전"""
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated, M

    def rotate_rect(self, rect, angle, center):
        """회전된 이미지의 사각형 좌표를 원본 이미지 좌표로 변환"""
        x, y, w, h = rect
        # 회전된 이미지의 4개 모서리 점
        points = np.array([
            [x, y],
            [x + w, y],
            [x + w, y + h],
            [x, y + h]
        ], dtype=np.float32)
        
        # 역회전 변환 행렬
        M_inv = cv2.getRotationMatrix2D(center, -angle, 1.0)
        # 역변환 적용
        points_transformed = cv2.transform(points.reshape(1, -1, 2), M_inv).reshape(-1, 2)
        
        # 바운딩 박스 계산
        x_min = max(0, int(np.min(points_transformed[:, 0])))
        y_min = max(0, int(np.min(points_transformed[:, 1])))
        x_max = int(np.max(points_transformed[:, 0]))
        y_max = int(np.max(points_transformed[:, 1]))
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)

    def read_file(self):
        cascade = cv2.CascadeClassifier(self._cascade_path)
        
        # cascade 파일이 제대로 로드되었는지 확인
        if cascade.empty():
            print(f"Cascade 파일을 로드할 수 없습니다: {self._cascade_path}")
            quit()
        
        img = cv2.imread(self._naul)
        
        # 이미지가 제대로 로드되었는지 확인
        if img is None:
            print(f"이미지를 로드할 수 없습니다: {self._naul}")
            quit()
        
        print(f"이미지 크기: {img.shape}")
        
        # 그레이스케일로 변환
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        
        face = None
        best_angle = 0
        
        # 다양한 각도로 회전하여 얼굴 인식 시도
        angles = [0, -15, -10, -5, 5, 10, 15, -20, 20, -25, 25]
        
        for angle in angles:
            if face is not None and len(face) > 0:
                break
                
            # 이미지 회전
            rotated_gray, _ = self.rotate_image(gray, angle)
            
            # 얼굴 인식 시도 (여러 파라미터 조합)
            face = cascade.detectMultiScale(rotated_gray, 
                                           scaleFactor=1.1, 
                                           minNeighbors=4, 
                                           minSize=(30, 30))
            
            if len(face) == 0:
                face = cascade.detectMultiScale(rotated_gray, 
                                               scaleFactor=1.05, 
                                               minNeighbors=3, 
                                               minSize=(20, 20))
            
            if len(face) > 0:
                best_angle = angle
                print(f"각도 {angle}도에서 얼굴을 찾았습니다!")
                # 회전된 좌표를 원본 이미지 좌표로 변환
                face_original = []
                for (x, y, w, h) in face:
                    rect_original = self.rotate_rect((x, y, w, h), angle, center)
                    face_original.append(rect_original)
                face = np.array(face_original)
                break
        
        if face is None or len(face) == 0:
            print("모든 각도에서 얼굴을 찾을 수 없습니다.")
            print("이미지를 저장하여 확인해보세요.")
            cv2.imwrite("naul_debug.png", img)
            quit()
        
        print(f"얼굴 {len(face)}개를 찾았습니다!")
        for idx, (x, y, w, h) in enumerate(face):
            print("얼굴인식 인덱스: ", idx)
            print("얼굴인식 좌표: ", x, y, w, h)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.imwrite("naul_face.png", img)
        cv2.imshow("naul-face.png", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    face_detect = FaceDetect()
    face_detect.read_file()

