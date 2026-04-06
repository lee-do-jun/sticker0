# 스티커 우클릭 메뉴: Copy / Paste

## Requirement Clarification Summary

### Before (Original)

> 스티커를 우클릭 하면, Menu에서 Copy와 Paste 기능 두개를 추가하고 싶습니다.

### After (Clarified)

**Goal**: 우클릭 컨텍스트 메뉴에 Copy·Paste를 추가한다. Copy는 스티커 본문을 시스템 클립보드로 보내고, Paste는 시스템 클립보드 내용을 **현재 우클릭한 스티커의 본문**에 반영한다. 새 스티커는 만들지 않는다.

**Scope (포함)**:

- 컨텍스트 메뉴 항목 Copy, Paste
- 클립보드 ↔ 스티커 본문(텍스트) 연동

**Scope (제외, 1차)**:

- 키보드 단축키(Ctrl+C / Ctrl+V 등)
- Copy로 “스티커 전체 복제” 후 Paste로 새 스티커 생성(앱 내부 복제 버퍼)

**Constraints / 동작**:

- Paste 시 클립보드를 읽을 수 없거나 비어 있으면 **조용히 무시**
- Copy 시 본문이 비어 있으면 **빈 문자열을 클립보드에 설정**

**Success Criteria**:

- 우클릭 메뉴에서 Copy로 스티커 텍스트가 OS 클립보드에 올라간다.
- 같은 메뉴에서 Paste로 클립보드 텍스트가 해당 스티커 본문에 반영된다(새 스티커 미생성).
- 위 엣지 케이스가 합의된 대로 동작한다.

**Decisions Made**:

| Question | Decision |
|----------|----------|
| Copy의 의미 | 스티커 본문 텍스트만 시스템 클립보드에 복사 |
| Paste의 의미 | 시스템 클립보드 텍스트를 **현재 스티커 본문**에 넣기(새 스티커 생성 없음) |
| 복제 스티커 배치 | 해당 없음(Paste는 새 스티커를 만들지 않음) |
| 단축키 | 1차는 우클릭 메뉴만 |
| Paste 실패/빈 클립보드 | 조용히 무시 |
| 빈 본문 Copy | 빈 문자열을 클립보드에 넣기 |

---

*Clarified via requirement workshop (vague), 2026-04-07.*
