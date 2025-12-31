import cv2
import numpy as np

class FaceDetect:
    def __init__(self):
        self._cascade_path = '../data/opencv/haarcascade_frontalface_alt.xml'
        self._bes = '../data/opencv/bes.jpg'

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
        
        img = cv2.imread(self._bes)
        
        # 이미지가 제대로 로드되었는지 확인
        if img is None:
            print(f"이미지를 로드할 수 없습니다: {self._bes}")
            quit()
        
        print(f"이미지 크기: {img.shape}")
        
        # 그레이스케일로 변환
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        
        best_face = None
        best_angle = 0
        max_faces = 0
        
        # 다양한 각도로 회전하여 얼굴 인식 시도
        angles = [0, -15, -10, -5, 5, 10, 15, -20, 20, -25, 25]
        
        # 여러 파라미터 조합 시도
        param_combinations = [
            {'scaleFactor': 1.1, 'minNeighbors': 3, 'minSize': (20, 20)},
            {'scaleFactor': 1.05, 'minNeighbors': 2, 'minSize': (15, 15)},
            {'scaleFactor': 1.1, 'minNeighbors': 2, 'minSize': (25, 25)},
            {'scaleFactor': 1.03, 'minNeighbors': 1, 'minSize': (10, 10)},
        ]
        
        for angle in angles:
            # 이미지 회전
            rotated_gray, _ = self.rotate_image(gray, angle)
            
            # 여러 파라미터 조합으로 시도
            for params in param_combinations:
                face = cascade.detectMultiScale(rotated_gray, **params)
                
                if len(face) > max_faces:
                    max_faces = len(face)
                    best_angle = angle
                    print(f"각도 {angle}도에서 {len(face)}개의 얼굴을 찾았습니다! (파라미터: {params})")
                    
                    # 회전된 좌표를 원본 이미지 좌표로 변환
                    face_original = []
                    for (x, y, w, h) in face:
                        rect_original = self.rotate_rect((x, y, w, h), angle, center)
                        face_original.append(rect_original)
                    best_face = np.array(face_original)
                    
                    # 4명을 모두 찾으면 중단
                    if max_faces >= 4:
                        break
            
            if max_faces >= 4:
                break
        
        face = best_face
        
        if face is None or len(face) == 0:
            print("모든 각도에서 얼굴을 찾을 수 없습니다.")
            print("이미지를 저장하여 확인해보세요.")
            cv2.imwrite("bes_debug.png", img)
            quit()
        
        # 중복 제거: 겹치는 사각형 제거
        def calculate_overlap(rect1, rect2):
            x1, y1, w1, h1 = rect1
            x2, y2, w2, h2 = rect2
            
            # 교집합 영역 계산
            left = max(x1, x2)
            top = max(y1, y2)
            right = min(x1 + w1, x2 + w2)
            bottom = min(y1 + h1, y2 + h2)
            
            if right < left or bottom < top:
                return 0
            
            intersection = (right - left) * (bottom - top)
            area1 = w1 * h1
            area2 = w2 * h2
            union = area1 + area2 - intersection
            
            return intersection / union if union > 0 else 0
        
        # 중복 제거
        filtered_faces = []
        for i, rect1 in enumerate(face):
            is_duplicate = False
            for j, rect2 in enumerate(filtered_faces):
                overlap = calculate_overlap(rect1, rect2)
                if overlap > 0.5:  # 50% 이상 겹치면 중복으로 간주
                    is_duplicate = True
                    # 더 큰 사각형을 유지
                    if (rect1[2] * rect1[3]) > (rect2[2] * rect2[3]):
                        filtered_faces[j] = rect1
                    break
            if not is_duplicate:
                filtered_faces.append(rect1)
        
        face = np.array(filtered_faces)
        print(f"얼굴 {len(face)}개를 찾았습니다! (중복 제거 후)")
        for idx, (x, y, w, h) in enumerate(face):
            print("얼굴인식 인덱스: ", idx)
            print("얼굴인식 좌표: ", x, y, w, h)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.imwrite("bes_face.png", img)
        cv2.imshow("bes-face.png", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    face_detect = FaceDetect()
    face_detect.read_file()

