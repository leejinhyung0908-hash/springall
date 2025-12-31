# 모델을 서버 시작 후 1번만 로딩하고 재사용합니다. 
# 6GB에서 필요한 옵션(슬라이싱/타일링) 기본 적용입니다.

import os
import torch

# torchvision DLL 오류 우회: transformers가 torchvision을 선택적으로 사용하도록 설정
# transformers는 torchvision이 없어도 작동할 수 있음
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

from core.config import MODEL_ID, DEVICE, DTYPE, HF_CACHE_DIR

_PIPELINE = None

def _torch_dtype():
    if DTYPE.lower() == "float16":
        return torch.float16
    if DTYPE.lower() == "bfloat16":
        return torch.bfloat16
    return torch.float32

def get_pipeline():
    global _PIPELINE
    if _PIPELINE is not None:
        return _PIPELINE

    # 지연 로딩: 실제 사용 시점에 diffusers를 import하여 호환성 문제 방지
    try:
        # 먼저 AutoPipelineForText2Image를 시도
        from diffusers import AutoPipelineForText2Image
        PipelineClass = AutoPipelineForText2Image
    except Exception as e:
        error_msg = str(e)
        if "DLL load failed" in error_msg or "_C" in error_msg or "지정된 프로시저를 찾을 수 없습니다" in error_msg:
            # AutoPipelineForText2Image가 실패하면 더 구체적인 파이프라인 시도
            # SDXL Turbo의 경우 StableDiffusionXLPipeline 사용
            try:
                print("⚠️ AutoPipelineForText2Image 로드 실패, StableDiffusionXLPipeline 시도 중...")
                from diffusers import StableDiffusionXLPipeline
                PipelineClass = StableDiffusionXLPipeline
            except Exception as e2:
                # 더 구체적인 오류 메시지와 해결 방법 제공
                raise RuntimeError(
                    f"DLL 로드 오류가 발생했습니다. torchvision의 C++ 확장 모듈을 로드할 수 없습니다.\n"
                    f"원본 오류: {error_msg}\n"
                    f"대체 시도 오류: {str(e2)}\n\n"
                    f"해결 방법 (순서대로 시도):\n"
                    f"1. Visual C++ 2015-2022 재배포 가능 패키지 설치 (필수):\n"
                    f"   https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
                    f"   설치 후 컴퓨터 재시작 필요\n"
                    f"2. torchvision 재설치:\n"
                    f"   pip uninstall torchvision -y\n"
                    f"   pip install torchvision --no-cache-dir\n"
                    f"3. conda 환경에서 재설치:\n"
                    f"   conda install pytorch torchvision torchaudio -c pytorch -y"
                ) from e2
        elif "AutoImageProcessor" in error_msg or "torchvision" in error_msg.lower():
            raise RuntimeError(
                f"라이브러리 호환성 오류가 발생했습니다. torch와 torchvision 버전이 맞지 않습니다.\n"
                f"오류: {error_msg}\n\n"
                f"해결 방법:\n"
                f"1. conda 환경에서: conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia\n"
                f"2. pip로: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121\n"
                f"3. 또는 requirements.txt의 버전을 확인하고 재설치하세요."
            ) from e
        else:
            raise
    
    dtype = _torch_dtype()

    try:
        pipe = PipelineClass.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            cache_dir=str(HF_CACHE_DIR),
            variant="fp16" if dtype in (torch.float16, torch.bfloat16) else None,
            use_safetensors=True,
        )
    except Exception as e:
        error_msg = str(e)
        if "AutoImageProcessor" in error_msg or "torchvision" in error_msg.lower():
            raise RuntimeError(
                f"파이프라인 로드 중 라이브러리 호환성 오류가 발생했습니다.\n"
                f"오류: {error_msg}\n\n"
                f"해결 방법: torch와 torchvision 버전을 호환되게 재설치하세요."
            ) from e
        raise

    # RTX 3050 6GB 안정 옵션
    try:
        pipe.enable_attention_slicing()  # 메모리 절약(속도 약간 감소)
    except Exception:
        pass

    try:
        pipe.enable_vae_tiling()  # 고해상도/VRAM 부족 시 안정
    except Exception:
        pass

    # 가능하면 xformers (설치되어 있을 때만)
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except Exception:
        pass

    # GPU 사용 확인 및 설정
    if DEVICE == "cuda" and torch.cuda.is_available():
        pipe = pipe.to("cuda")
        print(f"✅ GPU 사용: {torch.cuda.get_device_name(0)} (CUDA {torch.version.cuda})")
    else:
        pipe = pipe.to("cpu")
        if DEVICE == "cuda":
            print(f"⚠️ CUDA를 요청했지만 사용할 수 없어 CPU를 사용합니다.")
        else:
            print(f"ℹ️ CPU 모드로 실행됩니다.")

    _PIPELINE = pipe
    return _PIPELINE