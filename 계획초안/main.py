import io
import pretty_midi
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn

app = FastAPI(
    title="MIDI Parser API",
    description="Parses MIDI files and extracts raw data for LLM agents.",
    version="1.0.0"
)

@app.post("/parse")
async def parse_midi(file: UploadFile = File(...)):
    # 1. 파일 형식 검증
    if not file.filename.lower().endswith(('.mid', '.midi')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .mid or .midi file.")
    
    # 2. 파일 읽기 및 pretty_midi 로드 (에러 핸들링)
    try:
        content = await file.read()
        midi_data = pretty_midi.PrettyMIDI(io.BytesIO(content))
    except (IOError, EOFError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse or corrupted MIDI file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error while reading MIDI file: {str(e)}")

    # 3. 전역(Global) 메타데이터 추출
    try:
        bpm = float(midi_data.estimate_tempo())
    except Exception:
        bpm = 120.0  # 추정 불가 시 기본값

    total_length_seconds = float(midi_data.get_end_time())

    # 4. 트랙별 및 노트 데이터 추출
    tracks_data = []

    for instrument in midi_data.instruments:
        # 악기 이름 변환 (드럼 처리 포함)
        instr_name = "Drum Kit" if instrument.is_drum else pretty_midi.program_to_instrument_name(instrument.program)
        
        # LLM 컨텍스트 윈도우 보호를 위한 슬라이싱 (최대 100개)
        MAX_NOTES = 100
        notes_data = []
        for note in instrument.notes[:MAX_NOTES]:
            notes_data.append({
                "pitch": note.pitch,
                "velocity": note.velocity,
                "start": round(float(note.start), 4),
                "duration": round(float(note.end - note.start), 4)
            })

        tracks_data.append({
            "instrument_name": instr_name,
            "program_number": instrument.program,
            "is_drum": instrument.is_drum,
            "total_notes_in_track": len(instrument.notes), # 원래 총 개수 제공
            "parsed_notes_count": len(notes_data),         # 파싱된 개수
            "notes": notes_data
        })

    # 5. 최종 순수 JSON 응답 (분석 및 평가 제거)
    return {
        "global_info": {
            "bpm": round(bpm, 2),
            "total_length_seconds": round(total_length_seconds, 2)
        },
        "tracks": tracks_data
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
