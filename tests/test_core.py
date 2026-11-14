import json
from pathlib import Path
import pytest
from core import AIExplanation, Review, grade, sha256, simulate_actions, validate_sources
from storage import save_quiz, save_review, records

CONTENT=json.loads((Path(__file__).resolve().parents[1]/'data'/'content.json').read_text(encoding='utf-8'))

def test_lessons_have_valid_source_ids():
    for lesson in CONTENT['lessons']: validate_sources(lesson['source_ids'],CONTENT['sources'])
def test_all_quizzes_have_valid_answers():
    for lesson in CONTENT['lessons']:
        for q in lesson['questions']: assert q['answer'] in q['options']
def test_grade_all_correct():
    q=CONTENT['lessons'][0]['questions']; result=grade(q,{x['id']:x['answer'] for x in q});assert result['percentage']==100.0
def test_grade_wrong():
    q=CONTENT['lessons'][0]['questions']; result=grade(q,{x['id']:'WRONG' for x in q});assert result['correct']==0
def test_grade_empty(): assert grade([],{})['percentage']==0.0
def test_points(): assert simulate_actions(CONTENT['actions'],['A1','A5'])['learning_points']==7
def test_invalid_action():
    with pytest.raises(ValueError): simulate_actions(CONTENT['actions'],['BAD'])
def test_duplicate_action():
    with pytest.raises(ValueError): simulate_actions(CONTENT['actions'],['A1','A1'])
def test_hash_deterministic(): assert sha256({'b':2,'a':1})==sha256({'a':1,'b':2})
def test_invalid_source():
    with pytest.raises(ValueError): validate_sources(['INVALID'],CONTENT['sources'])
def test_ai_list_normalization():
    r=AIExplanation(explanation='A sufficiently detailed explanation.',everyday_example='Everyday example',key_takeaways='One idea',source_ids='S1');assert r.source_ids==['S1']
def test_review_validation():
    with pytest.raises(Exception): Review(decision='unknown',reviewer='Tester',notes='Notes')
def test_quiz_persistence(tmp_path):
    db=tmp_path/'data.db';save_quiz(db,'L1',{'correct':1,'total':2,'percentage':50});assert len(records(db,'quiz_runs'))==1
def test_review_persistence(tmp_path):
    db=tmp_path/'data.db';save_review(db,'L1',Review(decision='needs_revision',reviewer='Reviewer',notes='Check source'),{'text':'draft'});assert records(db,'ai_reviews')[0]['decision']=='needs_revision'
def test_table_allowlist(tmp_path):
    with pytest.raises(ValueError): records(tmp_path/'data.db','sqlite_master')
