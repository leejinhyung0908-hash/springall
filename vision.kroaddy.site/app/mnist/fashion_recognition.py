import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np

class FashionMnistTest:
    def __init__(self):
        self.class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
                           'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
    
    def create_model(self):
        # Fashion-MNIST 데이터셋 로드
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))  # 0-255를 -1~1로 정규화 (또는 ToTensor가 0-1로 변환)
        ])
        
        # 데이터를 numpy 배열로도 가져오기 위해 별도로 로드 (시각화용)
        train_dataset = datasets.FashionMNIST(
            root='./app/data/fashion-mnist',
            train=True,
            download=True,
            transform=transforms.ToTensor()
        )
        
        test_dataset = datasets.FashionMNIST(
            root='./app/data/fashion-mnist',
            train=False,
            download=True,
            transform=transforms.ToTensor()
        )
        
        # 데이터 로더 생성
        train_loader = DataLoader(train_dataset, batch_size=len(train_dataset), shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=len(test_dataset), shuffle=False)
        
        # 전체 데이터를 한 번에 가져오기 (시각화용)
        train_images, train_labels = next(iter(train_loader))
        test_images, test_labels = next(iter(test_loader))
        
        # 텐서를 numpy로 변환하고 정규화 (0-1 범위)
        train_images = train_images.numpy()
        train_labels = train_labels.numpy()
        test_images = test_images.numpy()
        test_labels = test_labels.numpy()
        
        # 이미지 정규화 (0-255 -> 0-1)
        train_images = train_images / 255.0
        test_images = test_images / 255.0
        
        # 이미지 shape: (60000, 1, 28, 28) -> (60000, 28, 28)
        train_images = train_images.squeeze(1)
        test_images = test_images.squeeze(1)
        
        # print('행: %d, 열: %d' % (train_images.shape[0], train_images.shape[1]))
        # print('행: %d, 열: %d' % (test_images.shape[0], test_images.shape[1]))
        
        # plt.figure()
        # plt.imshow(train_images[3])
        # plt.colorbar()
        # plt.grid(False)
        # plt.show()
        
        # 25개 이미지 시각화
        plt.figure(figsize=(10, 10))
        for i in range(25):
            plt.subplot(5, 5, i + 1)
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            plt.imshow(train_images[i], cmap=plt.cm.binary)
            plt.xlabel(self.class_names[train_labels[i]])
        # plt.show()
        
        # 모델 정의
        """
        relu (Rectified Linear Unit 정류한 선형 유닛)
        미분 가능한 0과 1사이의 값을 갖도록 하는 알고리즘
        softmax
        nn (neural network)의 최상위층에서 사용되며 classification을 위한 function
        결과를 확률값으로 해석하기 위한 알고리즘
        """
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = FashionMNISTNet().to(device)
        
        # 손실 함수 및 최적화 함수 정의
        criterion = nn.CrossEntropyLoss()  # sparse_categorical_crossentropy와 동일
        optimizer = optim.Adam(model.parameters())
        
        # 데이터 로더 재생성 (학습용)
        train_loader = DataLoader(
            datasets.FashionMNIST(
                root='./app/data/fashion-mnist',
                train=True,
                download=False,
                transform=transform
            ),
            batch_size=32,
            shuffle=True
        )
        
        test_loader = DataLoader(
            datasets.FashionMNIST(
                root='./app/data/fashion-mnist',
                train=False,
                download=False,
                transform=transform
            ),
            batch_size=32,
            shuffle=False
        )
        
        # 학습
        num_epochs = 5
        for epoch in range(num_epochs):
            model.train()
            total_loss = 0
            correct = 0
            total = 0
            
            for images, labels in train_loader:
                images = images.to(device)
                labels = labels.to(device)
                
                # 기울기 초기화
                optimizer.zero_grad()
                
                # 순전파
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                # 역전파 및 최적화
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
            
            train_acc = 100 * correct / total
            print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {total_loss/len(train_loader):.4f}, Accuracy: {train_acc:.2f}%')
        
        # 테스트
        model.eval()
        test_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in test_loader:
                images = images.to(device)
                labels = labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                test_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        test_acc = 100 * correct / total
        print(f'\n테스트 정확도: {test_acc:.2f}%')
        
        # 예측
        # 테스트 이미지를 모델에 입력하기 위해 텐서로 변환
        test_images_tensor = torch.from_numpy(test_images).float().unsqueeze(1)  # (10000, 28, 28) -> (10000, 1, 28, 28)
        test_images_tensor = test_images_tensor.to(device)
        
        model.eval()
        with torch.no_grad():
            outputs = model(test_images_tensor)
            predictions = torch.nn.functional.softmax(outputs, dim=1).cpu().numpy()
        
        print(predictions[3])
        
        # 10개 클래스에 대한 예측을 그래프화
        arr = [predictions, test_labels, test_images]
        return arr
    
    def plot_image(self, i, predictions_array, true_label, img):
        print(' === plot_image 로 진입 ===')
        predictions_array, true_label, img = predictions_array[i], true_label[i], img[i]
        plt.grid(False)
        plt.xticks([])
        plt.yticks([])
        
        plt.imshow(img, cmap=plt.cm.binary)
        # plt.show()
        predicted_label = np.argmax(predictions_array)
        if predicted_label == true_label:
            color = 'blue'
        else:
            color = 'red'
        
        plt.xlabel("{} {:2.0f}% ({})".format(self.class_names[predicted_label],
                                            100 * np.max(predictions_array),
                                            self.class_names[true_label]),
                  color=color)
    
    @staticmethod
    def plot_value_array(i, predictions_array, true_label):
        predictions_array, true_label = predictions_array[i], true_label[i]
        plt.grid(False)
        plt.xticks([])
        plt.yticks([])
        thisplot = plt.bar(range(10), predictions_array, color="#777777")
        plt.ylim([0, 1])
        predicted_label = np.argmax(predictions_array)
        
        thisplot[predicted_label].set_color('red')
        thisplot[true_label].set_color('blue')


class FashionMNISTNet(nn.Module):
    def __init__(self):
        super(FashionMNISTNet, self).__init__()
        # Flatten(input_shape=(28, 28)) -> Dense(128, activation='relu') -> Dense(10, activation='softmax')
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)
        # softmax는 CrossEntropyLoss에서 자동으로 처리되므로 forward에서는 생략
    
    def forward(self, x):
        x = self.flatten(x)  # (batch_size, 1, 28, 28) -> (batch_size, 784)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        # softmax는 예측 시에만 적용 (CrossEntropyLoss는 내부적으로 처리)
        return x


if __name__ == "__main__":
    fashion_test = FashionMnistTest()
    arr = fashion_test.create_model()
    predictions, test_labels, test_images = arr
    
    # 예시: 첫 번째 이미지 플롯
    fashion_test.plot_image(0, predictions, test_labels, test_images)
    plt.show()
    
    # 예시: 첫 번째 이미지의 예측값 배열 플롯
    fashion_test.plot_value_array(0, predictions, test_labels)
    plt.show()

