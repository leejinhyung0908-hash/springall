import cv2
import numpy as np

class LenaModel:
    def __init__(self):
        self._cascade_path = '../data/opencv/haarcascade_frontalface_alt.xml'
        self._lena = '../data/opencv/lena.jpg'

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
        
        img = cv2.imread(self._lena)
        
        # 이미지가 제대로 로드되었는지 확인
        if img is None:
            print(f"이미지를 로드할 수 없습니다: {self._lena}")
            quit()
        
        print(f"이미지 크기: {img.shape}")
        
        # 그레이스케일로 변환
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        
        # 정면 얼굴만 인식하도록 엄격한 파라미터 사용
        # minNeighbors를 높여서 확실한 얼굴만 인식 (5 이상 권장)
        # 회전 없이 0도만 사용 (정면 얼굴만)
        face = cascade.detectMultiScale(gray, 
                                       scaleFactor=1.1, 
                                       minNeighbors=5,  # 높은 값으로 확실한 얼굴만
                                       minSize=(30, 30),
                                       maxSize=(300, 300))  # 너무 큰 얼굴 제외
        
        if len(face) == 0:
            # 첫 시도 실패 시 약간 느슨한 파라미터로 재시도
            print("첫 번째 시도 실패. 약간 느슨한 파라미터로 재시도...")
            face = cascade.detectMultiScale(gray, 
                                           scaleFactor=1.1, 
                                           minNeighbors=4, 
                                           minSize=(25, 25),
                                           maxSize=(300, 300))
        
        # 정면 여성만 선택: 가장 큰 얼굴 또는 이미지 중앙에 가까운 얼굴
        if len(face) > 0:
            # 얼굴 크기(면적) 기준으로 정렬
            face_areas = [(x, y, w, h, w * h) for (x, y, w, h) in face]
            face_areas.sort(key=lambda f: f[4], reverse=True)  # 면적이 큰 순서로 정렬
            
            # 가장 큰 얼굴 선택 (정면 여성이 가장 크게 보일 것)
            largest_face = face_areas[0][:4]
            face = np.array([largest_face])
            
            print(f"정면 얼굴 1개를 찾았습니다!")
        
        if face is None or len(face) == 0:
            print("정면 얼굴을 찾을 수 없습니다.")
            print("이미지를 저장하여 확인해보세요.")
            cv2.imwrite("lena_debug.png", img)
            quit()
        
        # 원본 이미지에 사각형만 그리기 (original용)
        original_img = img.copy()
        for idx, (x, y, w, h) in enumerate(face):
            print("얼굴인식 인덱스: ", idx)
            print("얼굴인식 좌표: ", x, y, w, h)
            cv2.rectangle(original_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # 얼굴 영역만 그레이스케일로 변환
        gray_img = img.copy()
        for idx, (x, y, w, h) in enumerate(face):
            # 얼굴 영역을 그레이스케일로 변환
            face_region = gray[y:y+h, x:x+w]
            # 그레이스케일을 BGR로 변환 (3채널로 만들기 위해)
            face_region_bgr = cv2.cvtColor(face_region, cv2.COLOR_GRAY2BGR)
            # 원본 이미지의 얼굴 영역을 그레이스케일로 교체
            gray_img[y:y+h, x:x+w] = face_region_bgr
        
        # 얼굴 부분만 그레이스케일로 변환된 이미지 저장
        cv2.imwrite("lena_face.png", gray_img)
        
        # 원본 이미지(사각형만)와 얼굴 부분만 그레이스케일로 변환된 이미지, 얼굴 좌표 반환
        return original_img, gray_img, face
    
    def execute(self):
        # 얼굴 인식을 먼저 실행하고 이미지들 받기
        original_img, gray_img, face_coords = self.read_file()
        
        # original은 얼굴 인식만 (사각형만 그린 원본 이미지)
        # gray는 얼굴 부분만 그레이스케일로 변환된 이미지
        original = original_img  # 얼굴 인식만 (사각형만 그린 원본 이미지)
        grey = gray_img  # 얼굴 부분만 그레이스케일로 변환된 이미지
        unchange = original_img  # original과 동일 (얼굴 인식만)

        """
        이미지 읽기에는 위 3가지 속성이 존재함.
        대신에 1, 0, -1 을 사용해도 됨.
        """
        cv2.imshow('Original', original)
        cv2.imshow('Gray', grey)
        cv2.imshow('Unchanged', unchange)
        cv2.waitKey(0)
        cv2.destroyAllWindows() # 윈도우종료


if __name__ == "__main__":
    lena = LenaModel()
    lena.execute()

