/**
 * Player List Example
 * - React Query 제거됨 (UI 전용)
 */

'use client';

import { useState } from 'react';

export function PlayerListExample() {
  const [newPlayer, setNewPlayer] = useState({
    name: '',
    backNumber: 0,
    position: '',
    birthDate: '',
    nationality: '',
    height: 0,
    weight: 0,
    teamId: 1,
  });

  const handleCreate = () => {
    alert('선수 추가 기능은 react-query 제거로 인해 비활성화되었습니다.');
    // 폼 초기화
    setNewPlayer({
      name: '',
      backNumber: 0,
      position: '',
      birthDate: '',
      nationality: '',
      height: 0,
      weight: 0,
      teamId: 1,
    });
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">선수 목록</h1>
      
      {/* 선수 생성 폼 */}
      <div className="mb-6 p-4 border rounded">
        <h2 className="text-xl font-semibold mb-2">새 선수 추가</h2>
        <div className="grid grid-cols-2 gap-2">
          <input
            type="text"
            placeholder="이름"
            value={newPlayer.name}
            onChange={(e) => setNewPlayer({ ...newPlayer, name: e.target.value })}
            className="border p-2 rounded"
          />
          <input
            type="number"
            placeholder="등번호"
            value={newPlayer.backNumber}
            onChange={(e) => setNewPlayer({ ...newPlayer, backNumber: parseInt(e.target.value) })}
            className="border p-2 rounded"
          />
          <input
            type="text"
            placeholder="포지션"
            value={newPlayer.position}
            onChange={(e) => setNewPlayer({ ...newPlayer, position: e.target.value })}
            className="border p-2 rounded"
          />
          <input
            type="text"
            placeholder="국적"
            value={newPlayer.nationality}
            onChange={(e) => setNewPlayer({ ...newPlayer, nationality: e.target.value })}
            className="border p-2 rounded"
          />
        </div>
        <button
          onClick={handleCreate}
          className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          선수 추가
        </button>
      </div>
      
      {/* 선수 목록 */}
      <div className="grid gap-4">
        <p className="text-gray-500">선수 목록은 react-query 제거로 인해 표시되지 않습니다.</p>
      </div>
    </div>
  );
}

