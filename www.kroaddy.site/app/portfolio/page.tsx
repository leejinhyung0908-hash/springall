'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Upload, X, Image as ImageIcon, FileText, Tag, ArrowLeft, Check, Folder, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { API_BASE_URL } from '@/lib/api';

// CV 서버 URL (환경 변수 또는 기본값)
// NEXT_PUBLIC_API_BASE 또는 NEXT_PUBLIC_CV_API_BASE_URL 환경변수 사용
const CV_API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE ||
    process.env.NEXT_PUBLIC_CV_API_BASE_URL ||
    "http://localhost:8000";

export default function PortfolioUpload() {
    const router = useRouter();
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [tags, setTags] = useState('');

    interface FileInfo {
        file: File;
        preview: string;
        uploadTime: Date;
        detectedPreview?: string;
        faceCount?: number;
        faceCoordinates?: Array<{ index: number; x: number; y: number; w: number; h: number }>;
        isDetecting?: boolean;
        originalPath?: string; // 원본 파일 경로
        isAddedToPortfolio?: boolean; // 포트폴리오에 추가되었는지 여부
    }

    const [fileList, setFileList] = useState<FileInfo[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isDragging, setIsDragging] = useState(false);

    // 파일 처리 공통 함수
    const processFiles = (files: FileList | File[]) => {
        const fileArray = Array.isArray(files) ? files : Array.from(files);

        fileArray.forEach((file, index) => {
            // 파일 크기 체크 (10MB)
            if (file.size > 10 * 1024 * 1024) {
                alert(`${file.name} 파일이 10MB를 초과합니다.`);
                return;
            }

            // 이미지 파일 또는 PDF, TXT 파일 허용
            if (
                file.type.startsWith('image/') ||
                file.type === 'application/pdf' ||
                file.type === 'text/plain'
            ) {
                const uploadTime = new Date();

                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const newFileInfo: FileInfo = {
                            file,
                            preview: reader.result as string,
                            uploadTime,
                            isDetecting: false,
                            isAddedToPortfolio: false,
                        };
                        // 각 파일이 처리될 때마다 개별적으로 상태 업데이트
                        setFileList((prev) => [...prev, newFileInfo]);
                    };
                    reader.onerror = () => {
                        alert(`${file.name} 파일을 읽는 중 오류가 발생했습니다.`);
                    };
                    reader.readAsDataURL(file);
                } else {
                    // 이미지가 아닌 파일은 빈 미리보기로 즉시 추가
                    const newFileInfo: FileInfo = {
                        file,
                        preview: '',
                        uploadTime,
                    };
                    setFileList((prev) => [...prev, newFileInfo]);
                }
            } else {
                alert(`${file.name}은(는) 지원하지 않는 파일 형식입니다.`);
            }
        });
    };

    // 이미지 선택 핸들러
    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files) return;
        processFiles(files);
    };

    // 드래그 앤 드롭 핸들러
    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            processFiles(files);
        }
    };

    // 파일 제거 핸들러
    const handleRemoveFile = (index: number) => {
        setFileList((prev) => {
            const newList = prev.filter((_, i) => i !== index);
            // URL 해제
            if (prev[index].preview && !prev[index].preview.startsWith('data:') && prev[index].preview.startsWith('blob:')) {
                URL.revokeObjectURL(prev[index].preview);
            }
            return newList;
        });
    };

    // 모든 파일 삭제 핸들러
    const handleRemoveAllFiles = () => {
        if (fileList.length === 0) return;

        if (confirm('모든 파일을 삭제하시겠습니까?')) {
            // 모든 미리보기 URL 해제
            fileList.forEach((fileInfo) => {
                if (fileInfo.preview && !fileInfo.preview.startsWith('data:') && fileInfo.preview.startsWith('blob:')) {
                    URL.revokeObjectURL(fileInfo.preview);
                }
            });
            setFileList([]);
        }
    };

    // 파일 다운로드 핸들러
    const handleDownloadFile = async (fileInfo: FileInfo) => {
        try {
            // detect된 이미지가 있으면 서버의 app/data/yolo 폴더에 저장
            if (fileInfo.detectedPreview) {
                // base64 문자열을 Blob으로 변환
                const base64Data = fileInfo.detectedPreview.split(',')[1] || fileInfo.detectedPreview;
                const byteCharacters = atob(base64Data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: 'image/jpeg' });

                // 원본 파일명에서 확장자 추출
                const originalName = fileInfo.file.name;
                const nameWithoutExt = originalName.substring(0, originalName.lastIndexOf('.')) || originalName;
                const ext = originalName.substring(originalName.lastIndexOf('.')) || '.jpg';
                const detectedFileName = `${nameWithoutExt}_detected${ext}`;

                // multipart/form-data 형식으로 데이터 준비
                const formData = new FormData();
                formData.append('image', blob, detectedFileName);
                formData.append('filename', originalName);

                // 백엔드 API 호출하여 app/data/yolo 폴더에 저장 (multipart/form-data)
                const response = await fetch(`${CV_API_BASE_URL}/api/portfolio/save-detected-to-yolo`, {
                    method: 'POST',
                    body: formData,
                    // FormData를 사용하면 자동으로 multipart/form-data로 전송됨
                    // Content-Type 헤더를 명시적으로 설정하지 않음
                });

                const result = await response.json();

                if (result.success) {
                    alert(`✅ Detect된 이미지가 저장되었습니다!\n경로: ${result.saved_path}`);
                } else {
                    alert(`❌ 저장 실패: ${result.message}`);
                }
            } else {
                // detect된 이미지가 없으면 원본 파일 다운로드
                const url = URL.createObjectURL(fileInfo.file);
                const a = document.createElement('a');
                a.href = url;
                a.download = fileInfo.file.name;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('다운로드 오류:', error);
            alert('다운로드 중 오류가 발생했습니다.');
        }
    };

    // 파일 크기 포맷팅
    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    };

    // 날짜 포맷팅
    const formatDateTime = (date: Date): string => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = date.getHours();
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        const ampm = hours >= 12 ? '오후' : '오전';
        const displayHours = hours % 12 || 12;

        return `${year}.${month}.${day} ${ampm} ${displayHours}:${minutes}:${seconds}`;
    };

    // 포트폴리오 업로드 핸들러
    const handleUpload = async () => {
        if (!title.trim()) {
            alert('제목을 입력해주세요.');
            return;
        }

        if (fileList.length === 0) {
            alert('최소 1개 이상의 파일을 업로드해주세요.');
            return;
        }

        setIsUploading(true);
        setUploadProgress(0);

        try {
            // multipart/form-data 형식으로 데이터 준비
            const formData = new FormData();
            formData.append('title', title);
            formData.append('description', description);
            formData.append('tags', tags);

            fileList.forEach((fileInfo) => {
                formData.append(`images`, fileInfo.file);
            });

            const xhr = new XMLHttpRequest();
            // FormData를 사용하면 자동으로 multipart/form-data로 전송됨

            // 업로드 진행률 추적
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    setUploadProgress(percentComplete);
                }
            });

            // 업로드 완료 처리
            xhr.addEventListener('load', async () => {
                if (xhr.status === 200 || xhr.status === 201) {
                    setUploadProgress(100);
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            // 업로드된 파일들의 detect 결과를 fileList에 반영
                            if (response.files && Array.isArray(response.files)) {
                                response.files.forEach((uploadedFile: any, index: number) => {
                                    setFileList((prev) => {
                                        if (index < prev.length) {
                                            const updated = [...prev];
                                            const updateData: Partial<FileInfo> = {
                                                isAddedToPortfolio: true,
                                            };

                                            // detect된 이미지 정보가 있으면 추가
                                            if (uploadedFile.detected && uploadedFile.detected_image_base64) {
                                                updateData.detectedPreview = uploadedFile.detected_image_base64;
                                                updateData.faceCount = uploadedFile.face_count || 0;
                                                updateData.faceCoordinates = uploadedFile.face_coordinates || [];
                                            }

                                            updated[index] = {
                                                ...updated[index],
                                                ...updateData,
                                            };
                                            return updated;
                                        }
                                        return prev;
                                    });
                                });
                            }

                            alert(`포트폴리오가 성공적으로 추가되었습니다!\n${response.message}`);
                            // router.push('/mypage'); // 페이지 이동 제거
                        } else {
                            alert(`업로드 실패: ${response.message}`);
                            setIsUploading(false);
                        }
                    } catch (e) {
                        alert('포트폴리오가 성공적으로 추가되었습니다!');
                        setIsUploading(false);
                    }
                } else {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        alert(`업로드 실패: ${response.message || `HTTP ${xhr.status}`}`);
                    } catch (e) {
                        alert(`업로드 실패: HTTP ${xhr.status}`);
                    }
                    setIsUploading(false);
                }
            });

            // 에러 처리
            xhr.addEventListener('error', () => {
                alert('업로드 중 오류가 발생했습니다. 다시 시도해주세요.');
                setIsUploading(false);
                setUploadProgress(0);
            });

            // CV 서버로 파일 업로드
            xhr.open('POST', `${CV_API_BASE_URL}/api/portfolio/upload`);
            xhr.withCredentials = false; // CV 서버는 쿠키 불필요
            xhr.send(formData);
        } catch (error) {
            console.error('포트폴리오 업로드 오류:', error);
            alert('업로드 중 오류가 발생했습니다. 다시 시도해주세요.');
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8 relative overflow-hidden">
            {/* 배경 애니메이션 요소들 */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
                <div className="floating-circle floating-circle-1"></div>
                <div className="floating-circle floating-circle-2"></div>
                <div className="floating-circle floating-circle-3"></div>
            </div>

            {/* 메인 콘텐츠 */}
            <div className="w-full max-w-4xl relative z-10">
                {/* 헤더 */}
                <div className="mb-8 flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.back()}
                        className="hover:bg-gray-100"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <h1 className="text-3xl font-bold text-gray-900">포트폴리오 업로드</h1>
                </div>

                {/* 업로드 카드 */}
                <Card className="bg-white/80 backdrop-blur-sm border-gray-200/50 shadow-lg">
                    <CardHeader>
                        <CardTitle className="text-2xl">포트폴리오 업로드</CardTitle>
                        <CardDescription>
                            드래그 앤 드롭으로 파일을 업로드하거나 클릭하여 파일을 선택하세요
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* 제목 입력 */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                                <FileText className="w-4 h-4" />
                                제목
                            </label>
                            <Input
                                type="text"
                                placeholder="포트폴리오 제목을 입력하세요"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="w-full"
                            />
                        </div>

                        {/* 설명 입력 */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                                <FileText className="w-4 h-4" />
                                설명
                            </label>
                            <Textarea
                                placeholder="포트폴리오에 대한 설명을 입력하세요"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="w-full min-h-32"
                            />
                        </div>

                        {/* 태그 입력 */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                                <Tag className="w-4 h-4" />
                                태그 (쉼표로 구분)
                            </label>
                            <Input
                                type="text"
                                placeholder="예: 서울, 여행, 맛집"
                                value={tags}
                                onChange={(e) => setTags(e.target.value)}
                                className="w-full"
                            />
                        </div>

                        {/* 파일 업로드 */}
                        <div className="space-y-4">
                            <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                                <ImageIcon className="w-4 h-4" />
                                파일
                            </label>

                            {/* 드래그 앤 드롭 업로드 영역 */}
                            <div
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                onClick={() => fileInputRef.current?.click()}
                                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${isDragging
                                    ? 'border-blue-500 bg-blue-50/50 scale-[1.02]'
                                    : 'border-gray-300 hover:border-gray-400 bg-gray-50/50'
                                    }`}
                            >
                                <Folder className={`w-16 h-16 mx-auto mb-4 ${isDragging ? 'text-blue-500' : 'text-yellow-500'}`} />
                                <p className="text-lg font-medium text-gray-700 mb-2">
                                    파일을 여기에 드래그하세요
                                </p>
                                <p className="text-gray-600 mb-4">
                                    또는 클릭하여 파일을 선택하세요
                                </p>
                                <Button
                                    type="button"
                                    onClick={(e: React.MouseEvent<HTMLButtonElement>) => {
                                        e.stopPropagation();
                                        fileInputRef.current?.click();
                                    }}
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                >
                                    파일 선택
                                </Button>
                                <p className="text-sm text-gray-500 mt-4">
                                    지원 형식: JPG, PNG, GIF, WebP, PDF, TXT (최대 10MB)
                                </p>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    multiple
                                    accept="image/*,.pdf,.txt"
                                    onChange={handleImageSelect}
                                    className="hidden"
                                />
                            </div>

                            {/* 업로드된 파일 목록 */}
                            {fileList.length > 0 && (
                                <div className="mt-6">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                                        업로드된 파일 ({fileList.length}개)
                                    </h3>
                                    <div className="space-y-4">
                                        {fileList.map((fileInfo, index) => (
                                            <Card
                                                key={index}
                                                className="bg-white border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                                            >
                                                <CardContent className="p-4">
                                                    <div className="flex gap-4">
                                                        {/* 이미지 미리보기 또는 아이콘 */}
                                                        <div className="flex-shrink-0">
                                                            {fileInfo.file.type.startsWith('image/') && (fileInfo.detectedPreview || fileInfo.preview) ? (
                                                                <div className="relative w-20 h-20 rounded-lg overflow-hidden border border-gray-200 bg-gray-100">
                                                                    {fileInfo.isDetecting ? (
                                                                        <div className="w-full h-full flex items-center justify-center bg-gray-100">
                                                                            <span className="text-xs text-gray-500 animate-pulse">인식 중...</span>
                                                                        </div>
                                                                    ) : (
                                                                        <img
                                                                            src={fileInfo.detectedPreview || fileInfo.preview}
                                                                            alt={fileInfo.file.name}
                                                                            className="w-full h-full object-cover"
                                                                        />
                                                                    )}
                                                                    {fileInfo.faceCount && fileInfo.faceCount > 0 && (
                                                                        <div className="absolute top-1 right-1 bg-red-500 text-white text-xs px-1 rounded">
                                                                            {fileInfo.faceCount}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            ) : (
                                                                <div className="w-20 h-20 rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-center">
                                                                    {fileInfo.file.type.startsWith('image/') ? (
                                                                        <ImageIcon className="w-8 h-8 text-blue-500" />
                                                                    ) : (
                                                                        <FileText className="w-8 h-8 text-gray-500" />
                                                                    )}
                                                                </div>
                                                            )}
                                                        </div>

                                                        {/* 파일 정보 */}
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-start justify-between gap-2">
                                                                <div className="min-w-0 flex-1">
                                                                    <div className="flex items-center gap-2 mb-1">
                                                                        {!fileInfo.file.type.startsWith('image/') && (
                                                                            <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                                                                        )}
                                                                        <p className="font-medium text-gray-900 truncate">
                                                                            {fileInfo.file.name}
                                                                        </p>
                                                                    </div>
                                                                    <p className="text-sm text-gray-500 mb-1">
                                                                        {formatFileSize(fileInfo.file.size)}
                                                                    </p>
                                                                    <p className="text-xs text-gray-400 mb-1">
                                                                        {formatDateTime(fileInfo.uploadTime)}
                                                                    </p>
                                                                    {fileInfo.isAddedToPortfolio && (
                                                                        <p className="text-xs text-green-600 font-medium">
                                                                            ✓ 추가된 포트폴리오
                                                                        </p>
                                                                    )}
                                                                </div>

                                                                {/* 액션 버튼들 */}
                                                                <div className="flex flex-col gap-2 flex-shrink-0">
                                                                    <button
                                                                        onClick={() => handleRemoveFile(index)}
                                                                        className="w-6 h-6 flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                                                                        title="삭제"
                                                                    >
                                                                        <X className="w-4 h-4" />
                                                                    </button>
                                                                    <Button
                                                                        variant="outline"
                                                                        size="sm"
                                                                        onClick={() => handleDownloadFile(fileInfo)}
                                                                        className="text-xs px-2 py-1 h-auto"
                                                                        title="다운로드"
                                                                        disabled={!fileInfo.isAddedToPortfolio}
                                                                    >
                                                                        <Download className="w-3 h-3" />
                                                                    </Button>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* 업로드 진행률 */}
                        {isUploading && (
                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-sm text-gray-600">
                                    <span>업로드 중...</span>
                                    <span>{Math.round(uploadProgress)}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                            </div>
                        )}

                        {/* 액션 버튼 */}
                        <div className="flex flex-col gap-4 pt-6 border-t border-gray-200">
                            <div className="flex gap-4">
                                <Button
                                    variant="outline"
                                    onClick={handleRemoveAllFiles}
                                    disabled={isUploading || fileList.length === 0}
                                    className="flex-1"
                                >
                                    <X className="w-4 h-4 mr-2" />
                                    모든 파일 삭제
                                </Button>
                                <Button
                                    onClick={handleUpload}
                                    disabled={isUploading || !title.trim() || fileList.length === 0}
                                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                                >
                                    {isUploading ? (
                                        <>
                                            <span className="animate-spin mr-2">⏳</span>
                                            업로드 중...
                                        </>
                                    ) : (
                                        <>
                                            <Check className="w-4 h-4 mr-2" />
                                            포트폴리오에 추가 ({fileList.length})
                                        </>
                                    )}
                                </Button>
                            </div>
                            <Button
                                variant="outline"
                                onClick={() => router.back()}
                                disabled={isUploading}
                                className="w-full"
                            >
                                <ArrowLeft className="w-4 h-4 mr-2" />
                                이전 페이지로
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

