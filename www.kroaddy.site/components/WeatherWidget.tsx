// @ts-nocheck
"use client";

import React, { useState, useEffect } from 'react';
import { Cloud, Sun, CloudRain, CloudSnow, Wind } from 'lucide-react';

interface WeatherData {
    temp: number;
    description: string;
    icon: string;
    city: string;
}

interface WeatherWidgetProps {
    onWeatherUpdate?: (weather: { temp: number; description: string; city: string }) => void;
    onLocationUpdate?: (location: { lat: number; lng: number }) => void;
}

export function WeatherWidget({ onWeatherUpdate, onLocationUpdate }: WeatherWidgetProps = {}) {
    const [weather, setWeather] = useState<WeatherData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchWeather = async () => {
            try {
                setLoading(true);
                // 사용자 위치 가져오기
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        async (position) => {
                            const { latitude, longitude } = position.coords;
                            
                            // 위치 정보를 부모 컴포넌트로 전달
                            if (onLocationUpdate) {
                                onLocationUpdate({ lat: latitude, lng: longitude });
                            }
                            
                            const response = await fetch(
                                `/api/weather?lat=${latitude}&lon=${longitude}`
                            );

                            if (!response.ok) {
                                throw new Error('날씨 정보를 가져올 수 없습니다');
                            }

                            const data = await response.json();
                            setWeather(data);
                            setLoading(false);
                            
                            // 날씨 정보를 부모 컴포넌트로 전달
                            if (onWeatherUpdate) {
                                onWeatherUpdate({
                                    temp: data.temp,
                                    description: data.description,
                                    city: data.city
                                });
                            }
                        },
                        (err) => {
                            // 위치 권한이 거부된 경우 서울 기본값 사용
                            fetchWeatherByCity('Seoul');
                        }
                    );
                } else {
                    // Geolocation을 지원하지 않는 경우 서울 기본값 사용
                    fetchWeatherByCity('Seoul');
                }
            } catch (err) {
                setError('날씨 정보를 불러올 수 없습니다');
                setLoading(false);
            }
        };

        const fetchWeatherByCity = async (city: string) => {
            try {
                const response = await fetch(`/api/weather?city=${city}`);
                if (!response.ok) {
                    throw new Error('날씨 정보를 가져올 수 없습니다');
                }
                const data = await response.json();
                setWeather(data);
                setLoading(false);
                
                // 날씨 정보를 부모 컴포넌트로 전달
                if (onWeatherUpdate) {
                    onWeatherUpdate({
                        temp: data.temp,
                        description: data.description,
                        city: data.city
                    });
                }
            } catch (err) {
                setError('날씨 정보를 불러올 수 없습니다');
                setLoading(false);
            }
        };

        fetchWeather();

        // 10분마다 업데이트
        const interval = setInterval(fetchWeather, 600000);
        return () => clearInterval(interval);
    }, []);

    const getWeatherIcon = (description: string) => {
        const desc = description.toLowerCase();
        if (desc.includes('rain') || desc.includes('drizzle')) {
            return <CloudRain className="w-5 h-5 text-blue-500" />;
        } else if (desc.includes('snow')) {
            return <CloudSnow className="w-5 h-5 text-gray-400" />;
        } else if (desc.includes('cloud')) {
            return <Cloud className="w-5 h-5 text-gray-500" />;
        } else {
            return <Sun className="w-5 h-5 text-yellow-500" />;
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center gap-1.5 px-3 py-2.5 bg-white/90 backdrop-blur-sm rounded-xl shadow-md border border-gray-200">
                <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin"></div>
                <span className="text-[10px] text-gray-500">Loading...</span>
            </div>
        );
    }

    if (error || !weather) {
        return null; // 에러 시 표시하지 않음
    }

    return (
        <div className="flex flex-row items-center gap-3 px-4 py-2.5 bg-white/90 backdrop-blur-sm rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow min-w-[140px]">
            {getWeatherIcon(weather.description)}
            <div className="flex flex-col">
                <span className="text-sm font-semibold text-gray-800">
                    {Math.round(weather.temp)}°
                </span>
                <span className="text-[10px] text-gray-600 leading-tight whitespace-nowrap">
                    {weather.city.length > 15 ? weather.city.substring(0, 15) + '...' : weather.city}
                </span>
            </div>
        </div>
    );
}

