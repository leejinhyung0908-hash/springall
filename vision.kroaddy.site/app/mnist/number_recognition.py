# 머신러닝 학습의 Hello World 와 같은 MNIST(손글씨 숫자 인식) 문제를 신경망으로 풀어봅니다.
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# 신경망 모델 정의
class MNISTNet(nn.Module):
    def __init__(self):
        super(MNISTNet, self).__init__()
        # 784(입력 특성값) -> 256 (히든레이어 뉴런 갯수) -> 256 (히든레이어 뉴런 갯수) -> 10 (결과값 0~9 분류)
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 10)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # 입력값을 평탄화 (배치 크기, 784)
        x = x.view(-1, 784)
        # 첫 번째 레이어: ReLU 활성화 함수 적용
        x = self.relu(self.fc1(x))
        # 두 번째 레이어: ReLU 활성화 함수 적용
        x = self.relu(self.fc2(x))
        # 최종 출력 레이어 (10개의 분류)
        x = self.fc3(x)
        return x

def train_model(model, train_loader, optimizer, criterion, device):
    """모델 학습 함수"""
    model.train()
    total_cost = 0
    total_batch = len(train_loader)
    
    for batch_xs, batch_ys in train_loader:
        # 데이터를 디바이스로 이동
        batch_xs = batch_xs.to(device)
        batch_ys = batch_ys.to(device)
        
        # 기울기 초기화
        optimizer.zero_grad()
        
        # 순전파
        outputs = model(batch_xs)
        loss = criterion(outputs, batch_ys)
        
        # 역전파 및 최적화
        loss.backward()
        optimizer.step()
        
        total_cost += loss.item()
    
    return total_cost / total_batch

def evaluate_model(model, test_loader, device):
    """모델 평가 함수"""
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = 100 * correct / total
    return accuracy

if __name__ == "__main__":
    # 디바이스 설정 (GPU 사용 가능하면 GPU, 아니면 CPU)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'사용 디바이스: {device}')
    
    # 데이터 변환 정의
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))  # MNIST 데이터셋의 평균과 표준편차
    ])
    
    # MNIST 데이터셋 로드
    # 지정한 폴더에 MNIST 데이터가 없는 경우 자동으로 데이터를 다운로드합니다.
    train_dataset = datasets.MNIST(
        root='./app/data/number-mnist',
        train=True,
        download=True,
        transform=transform
    )
    
    test_dataset = datasets.MNIST(
        root='./app/data/number-mnist',
        train=False,
        download=True,
        transform=transform
    )
    
    # 데이터 로더 생성
    batch_size = 100
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False
    )
    
    # 모델 생성 및 디바이스로 이동
    model = MNISTNet().to(device)
    
    # 손실 함수 및 최적화 함수 정의
    criterion = nn.CrossEntropyLoss()  # softmax_cross_entropy_with_logits_v2와 동일
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 신경망 모델 학습
    num_epochs = 15
    for epoch in range(num_epochs):
        avg_cost = train_model(model, train_loader, optimizer, criterion, device)
        print('Epoch:', '%04d' % (epoch + 1),
              'Avg. cost =', '{:.3f}'.format(avg_cost))
    
    print('최적화 완료!')
    
    # 결과 확인
    accuracy = evaluate_model(model, test_loader, device)
    print(f'정확도: {accuracy:.2f}%')

