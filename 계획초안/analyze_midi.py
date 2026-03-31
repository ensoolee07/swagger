import pretty_midi
import argparse
import sys
import os

def analyze_midi(file_path):
    if not os.path.exists(file_path):
        print(f"Error: 파일 '{file_path}'을(를) 찾을 수 없습니다.")
        sys.exit(1)
        
    try:
        # MIDI 파일 로드
        print(f"'{file_path}' 파일을 로드 중입니다...")
        midi_data = pretty_midi.PrettyMIDI(file_path)
        
        print(f"\n=== MIDI 파일 분석 결과: {os.path.basename(file_path)} ===")
        print(f"- 총 재생 시간: {midi_data.get_end_time():.2f} 초")
        
        # 템포 정보 분석
        tempos = midi_data.get_tempo_changes()
        if len(tempos[0]) > 0:
            print(f"- 초기 템포: {tempos[1][0]:.2f} BPM")
            if len(tempos[0]) > 1:
                print(f"- 템포 변경 횟수: {len(tempos[0]) - 1} 회")
        else:
            print("- 템포 정보: 없음")
            
        # 조표(Key Signature) 변화
        key_changes = midi_data.key_signature_changes
        print(f"- 조표 변경 횟수: {len(key_changes)} 회")
        for i, ks in enumerate(key_changes):
            print(f"  [{i+1}] 시작 시간 {ks.time:.2f}초: {pretty_midi.key_number_to_key_name(ks.key_number)}")
            
        # 박자 기호(Time Signature) 변화
        time_changes = midi_data.time_signature_changes
        print(f"- 박자 기호 변경 횟수: {len(time_changes)} 회")
        for i, ts in enumerate(time_changes):
            print(f"  [{i+1}] 시작 시간 {ts.time:.2f}초: {ts.numerator}/{ts.denominator}")
            
        print("\n=== 악기(Track) 정보 ===")
        print(f"- 총 악기(트랙) 수: {len(midi_data.instruments)}")
        
        for idx, instrument in enumerate(midi_data.instruments):
            # 악기 이름 찾기 (드럼이 아닌 경우 GM 악기 이름. 드럼인 경우 'Drum Kit')
            if instrument.is_drum:
                instrument_name = "Drum Kit"
            else:
                instrument_name = pretty_midi.program_to_instrument_name(instrument.program)
                
            print(f"\n[트랙 {idx+1}] {instrument.name if instrument.name else '이름 없음'}")
            print(f"  - 악기 종류: {instrument_name} (Program {instrument.program})")
            print(f"  - 드럼 여부: {'예' if instrument.is_drum else '아니오'}")
            print(f"  - 총 노트 수: {len(instrument.notes)} 개")
            
            if len(instrument.notes) > 0:
                # 피치(음높이) 범위 확인
                pitches = [note.pitch for note in instrument.notes]
                min_pitch = min(pitches)
                max_pitch = max(pitches)
                
                print(f"  - 가장 낮은 피치: {min_pitch} ({pretty_midi.note_number_to_name(min_pitch)})")
                print(f"  - 가장 높은 피치: {max_pitch} ({pretty_midi.note_number_to_name(max_pitch)})")
                
                # 볼륨(Velocity) 평균
                velocities = [note.velocity for note in instrument.notes]
                avg_velocity = sum(velocities) / len(velocities)
                print(f"  - 평균 볼륨(Velocity): {avg_velocity:.1f}")
                
            if len(instrument.pitch_bends) > 0:
                print(f"  - 피치 벤드(Pitch Bend) 이벤트 수: {len(instrument.pitch_bends)}")
                
            if len(instrument.control_changes) > 0:
                print(f"  - 컨트롤 체인지(Control Change) 이벤트 수: {len(instrument.control_changes)}")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MIDI 파일 분석 스크립트")
    parser.add_argument("midi_file", help="분석할 MIDI 파일의 경로")
    args = parser.parse_args()
    
    analyze_midi(args.midi_file)
