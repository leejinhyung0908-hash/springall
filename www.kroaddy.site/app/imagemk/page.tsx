'use client';

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Loader2, Download, Sparkles } from "lucide-react";

const DIFFUSERS_API_URL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

interface GenerateRequest {
    prompt: string;
    negative_prompt?: string;
    width?: number;
    height?: number;
    steps?: number;
    guidance_scale?: number;
    seed?: number;
}

interface GenerateResponse {
    id: string;
    image_url: string;
    meta_url: string;
    meta: {
        prompt: string;
        width: number;
        height: number;
        steps: number;
        seed?: number;
    };
}

export default function ImageMKPage() {
    const [prompt, setPrompt] = useState("");
    const [negativePrompt, setNegativePrompt] = useState("");
    const [width, setWidth] = useState(768);
    const [height, setHeight] = useState(768);
    const [steps, setSteps] = useState(4);
    const [guidanceScale, setGuidanceScale] = useState(0.0);
    const [seed, setSeed] = useState<number | undefined>(undefined);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<GenerateResponse | null>(null);

    const handleGenerate = async () => {
        if (!prompt.trim()) {
            setError("프롬프트를 입력해주세요.");
            return;
        }

        setIsGenerating(true);
        setError(null);
        setGeneratedImage(null);
        setResult(null);

        try {
            const requestBody: GenerateRequest = {
                prompt: prompt.trim(),
                width,
                height,
                steps,
                guidance_scale: guidanceScale,
            };

            if (negativePrompt.trim()) {
                requestBody.negative_prompt = negativePrompt.trim();
            }

            if (seed !== undefined && seed !== null) {
                requestBody.seed = seed;
            }

            const response = await fetch(`${DIFFUSERS_API_URL}/api/v1/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data: GenerateResponse = await response.json();
            setResult(data);

            // 이미지 URL이 상대 경로인 경우 절대 경로로 변환
            let imageUrl = data.image_url;
            if (!imageUrl.startsWith('http')) {
                // 상대 경로인 경우 절대 경로로 변환
                imageUrl = `${DIFFUSERS_API_URL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;
            }

            console.log('생성된 이미지 URL:', imageUrl);
            setGeneratedImage(imageUrl);
        } catch (err) {
            setError(err instanceof Error ? err.message : '이미지 생성 중 오류가 발생했습니다.');
            console.error('이미지 생성 오류:', err);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleDownload = () => {
        if (generatedImage) {
            window.open(generatedImage, '_blank');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
            {/* 헤더 */}
            <div className="sticky top-0 z-50 bg-gray-900/80 backdrop-blur-sm border-b border-gray-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <Link
                            href="/"
                            className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            <span>홈으로</span>
                        </Link>
                        <h1 className="text-xl font-bold flex items-center gap-2">
                            <Sparkles className="w-6 h-6 text-blue-400" />
                            AI 이미지 생성
                        </h1>
                        <div className="w-20"></div> {/* 공간 균형 */}
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* 왼쪽: 입력 폼 */}
                    <div className="space-y-6">
                        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
                            <h2 className="text-2xl font-bold mb-6">이미지 생성 설정</h2>

                            {/* 프롬프트 입력 */}
                            <div className="mb-6">
                                <label className="block text-sm font-medium mb-2">
                                    프롬프트 <span className="text-red-400">*</span>
                                </label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    onKeyDown={(e) => {
                                        // Ctrl+Enter 또는 Cmd+Enter로 생성
                                        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                                            e.preventDefault();
                                            if (!isGenerating && prompt.trim()) {
                                                handleGenerate();
                                            }
                                        }
                                    }}
                                    placeholder="예: a cute robot barista, cinematic lighting&#10;Ctrl+Enter 또는 Cmd+Enter로 빠르게 생성"
                                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                    rows={4}
                                    disabled={isGenerating}
                                />
                            </div>

                            {/* 네거티브 프롬프트 */}
                            <div className="mb-6">
                                <label className="block text-sm font-medium mb-2">
                                    네거티브 프롬프트 (선택)
                                </label>
                                <textarea
                                    value={negativePrompt}
                                    onChange={(e) => setNegativePrompt(e.target.value)}
                                    placeholder="예: blurry, low quality, distorted"
                                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                    rows={3}
                                    disabled={isGenerating}
                                />
                            </div>

                            {/* 설정 그리드 */}
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div>
                                    <label className="block text-sm font-medium mb-2">너비</label>
                                    <input
                                        type="number"
                                        value={width}
                                        onChange={(e) => setWidth(parseInt(e.target.value) || 768)}
                                        min={64}
                                        max={1024}
                                        step={64}
                                        className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        disabled={isGenerating}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">높이</label>
                                    <input
                                        type="number"
                                        value={height}
                                        onChange={(e) => setHeight(parseInt(e.target.value) || 768)}
                                        min={64}
                                        max={1024}
                                        step={64}
                                        className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        disabled={isGenerating}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">스텝</label>
                                    <input
                                        type="number"
                                        value={steps}
                                        onChange={(e) => setSteps(parseInt(e.target.value) || 4)}
                                        min={1}
                                        max={50}
                                        className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        disabled={isGenerating}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Guidance Scale</label>
                                    <input
                                        type="number"
                                        value={guidanceScale}
                                        onChange={(e) => setGuidanceScale(parseFloat(e.target.value) || 0.0)}
                                        min={0}
                                        max={20}
                                        step={0.1}
                                        className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        disabled={isGenerating}
                                    />
                                </div>
                            </div>

                            {/* 시드 */}
                            <div className="mb-6">
                                <label className="block text-sm font-medium mb-2">
                                    시드 (선택, 재현성을 위해)
                                </label>
                                <input
                                    type="number"
                                    value={seed || ''}
                                    onChange={(e) => setSeed(e.target.value ? parseInt(e.target.value) : undefined)}
                                    placeholder="비워두면 랜덤"
                                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    disabled={isGenerating}
                                />
                            </div>

                            {/* 생성 버튼 */}
                            <button
                                onClick={handleGenerate}
                                disabled={isGenerating || !prompt.trim()}
                                className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg font-semibold text-white transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {isGenerating ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>생성 중...</span>
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-5 h-5" />
                                        <span>이미지 생성</span>
                                    </>
                                )}
                            </button>

                            {/* 오류 메시지 */}
                            {error && (
                                <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
                                    <p className="font-medium">오류</p>
                                    <p className="text-sm mt-1">{error}</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* 오른쪽: 결과 표시 */}
                    <div className="space-y-6">
                        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
                            <h2 className="text-2xl font-bold mb-6">생성된 이미지</h2>

                            {isGenerating && (
                                <div className="flex flex-col items-center justify-center py-20">
                                    <Loader2 className="w-16 h-16 animate-spin text-blue-400 mb-4" />
                                    <p className="text-gray-400">이미지를 생성하고 있습니다...</p>
                                    <p className="text-sm text-gray-500 mt-2">잠시만 기다려주세요</p>
                                </div>
                            )}

                            {!isGenerating && !generatedImage && (
                                <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                                    <Sparkles className="w-16 h-16 mb-4 opacity-50" />
                                    <p>왼쪽에서 프롬프트를 입력하고 생성 버튼을 클릭하세요</p>
                                </div>
                            )}

                            {generatedImage && (
                                <div className="space-y-4">
                                    <div className="relative aspect-square bg-gray-900 rounded-lg overflow-hidden border border-gray-700">
                                        <img
                                            src={generatedImage}
                                            alt="Generated image"
                                            className="w-full h-full object-contain"
                                            onError={(e) => {
                                                console.error('이미지 로드 실패:', generatedImage);
                                                setError('이미지를 불러올 수 없습니다. URL을 확인해주세요.');
                                            }}
                                        />
                                    </div>

                                    {result && (
                                        <div className="space-y-2 text-sm">
                                            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                                                <span className="text-gray-400">ID:</span>
                                                <span className="font-mono text-xs">{result.id}</span>
                                            </div>
                                            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                                                <span className="text-gray-400">크기:</span>
                                                <span>{result.meta.width} × {result.meta.height}</span>
                                            </div>
                                            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                                                <span className="text-gray-400">스텝:</span>
                                                <span>{result.meta.steps}</span>
                                            </div>
                                            {result.meta.seed !== undefined && (
                                                <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                                                    <span className="text-gray-400">시드:</span>
                                                    <span className="font-mono">{result.meta.seed}</span>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    <button
                                        onClick={handleDownload}
                                        className="w-full py-3 px-6 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold text-white transition-colors flex items-center justify-center gap-2"
                                    >
                                        <Download className="w-5 h-5" />
                                        <span>이미지 다운로드</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

