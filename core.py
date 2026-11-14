"""Deterministic learning and simulation functions. No AI is required."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class AIExplanation(BaseModel):
    explanation: str = Field(min_length=10)
    everyday_example: str = Field(min_length=5)
    key_takeaways: list[str] = Field(min_length=1, max_length=5)
    source_ids: list[str] = Field(min_length=1)
    limitations: list[str] = Field(default_factory=list)
    @field_validator('key_takeaways','source_ids','limitations',mode='before')
    @classmethod
    def normalize_list(cls, v):
        if isinstance(v,str): return [v]
        return v

class Review(BaseModel):
    decision: Literal['approved','needs_revision','rejected']
    reviewer: str = Field(min_length=2)
    notes: str = Field(min_length=3)

def sha256(data: object) -> str:
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()

def grade(questions: list[dict], answers: dict[str,str]) -> dict:
    if not questions: return {'correct':0,'total':0,'percentage':0.0,'details':[]}
    details=[]
    for q in questions:
        chosen=answers.get(q['id'])
        details.append({'id':q['id'],'question':q['question'],'chosen':chosen,'correct_answer':q['answer'], 'is_correct':chosen==q['answer'],'feedback':q['feedback']})
    correct=sum(d['is_correct'] for d in details)
    return {'correct':correct,'total':len(questions),'percentage':round(100*correct/len(questions),1),'details':details}

def simulate_actions(actions: list[dict], selected: list[str]) -> dict:
    """Illustrative points, NOT emissions, financial savings or predicted climate impact."""
    ids={a['id'] for a in actions}
    if len(set(selected))!=len(selected) or not set(selected).issubset(ids):
        raise ValueError('Invalid or duplicate action IDs')
    chosen=[a for a in actions if a['id'] in selected]
    return {'selected':selected,'learning_points':sum(int(a['points']) for a in chosen),
            'categories':sorted(set(a['category'] for a in chosen)),
            'note':'Educational game points only; not an estimate of avoided emissions or real-world impact.'}

def validate_sources(source_ids: list[str], sources: list[dict]) -> None:
    valid={s['id'] for s in sources}
    if not source_ids or any(s not in valid for s in source_ids):
        raise ValueError('AI response refers to missing source IDs')

def utc_now(): return datetime.now(timezone.utc).isoformat()
