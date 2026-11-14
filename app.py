"""COP31 AI Solutions Lab Day 6 — independent educational Streamlit app."""
import json, os
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from core import AIExplanation, Review, grade, simulate_actions, sha256
from ai_gateway import explain_with_gemini
from storage import init_db, save_quiz, save_review, records

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')
CONTENT=json.loads((ROOT/'data'/'content.json').read_text(encoding='utf-8'))
LESSONS=CONTENT['lessons']; SOURCES=CONTENT['sources']; ACTIONS=CONTENT['actions']
DB=ROOT/'local_data'/'learning.sqlite3'
init_db(DB)
st.set_page_config(page_title='Climate Education & Youth Engagement Lab',page_icon='🌱',layout='wide')
st.markdown('''<style>
.stApp {background: #071d1a; color:#e6f4ed;}
[data-testid="stHeader"] {background:#071d1a;}
[data-testid="stSidebar"] {background:#103129;}
div[data-testid="stMetric"] {background:#123c31;border:1px solid #316e55;border-radius:12px;padding:14px;}
h1,h2,h3 {color:#c5f2d3!important;}
.stButton button[kind="primary"] {background:#2e8b61;color:white;}
</style>''',unsafe_allow_html=True)
st.title('🌍 Climate Education & Youth Engagement Lab V1.0')
st.caption('COP31 AI Solutions Lab · Day 6 · November 14, 2026 · Independent educational prototype')
st.info('For general audiences. No personal data about children is requested. AI explanations are drafts requiring human review. All action points are illustrative.')
if 'quiz_results' not in st.session_state: st.session_state.quiz_results={}
if 'ai_output' not in st.session_state: st.session_state.ai_output=None
if 'ai_lesson' not in st.session_state: st.session_state.ai_lesson=None

tabs=st.tabs(['📊 Overview','📚 Learning Hub','🧩 Climate Quiz','🌱 Youth Action Lab','🤖 AI & Human Review','📤 Progress & Export'])
with tabs[0]:
    st.subheader('Climate literacy starts with evidence')
    a,b,c=st.columns(3)
    a.metric('Learning lessons',len(LESSONS)); b.metric('Quiz questions',sum(len(l['questions']) for l in LESSONS)); c.metric('Action scenarios',len(ACTIONS))
    st.markdown('**Learning pathway:** Theory → Everyday example → Quiz → Action simulation → AI-assisted explanation → Human review')
    st.write('This application supports climate education and youth engagement without collecting student identities or claiming verified learning outcomes.')
    st.dataframe(pd.DataFrame([{'Lesson':l['title'],'Level':l['level'],'Questions':len(l['questions'])} for l in LESSONS]),hide_index=True,use_container_width=True)
with tabs[1]:
    st.subheader('Climate Learning Hub')
    lesson=st.selectbox('Choose a lesson',[l['title'] for l in LESSONS],key='learning_choice')
    l=next(x for x in LESSONS if x['title']==lesson)
    st.markdown(f"### {l['title']}")
    st.write('**Theory:**',l['concept'])
    st.write('**Everyday analogy:**',l['analogy'])
    st.write('**Practical example:**',l['example'])
    st.markdown('**Reference material**')
    for s in SOURCES:
        if s['id'] in l['source_ids']:
            st.markdown(f"- [{s['title']}]({s['url']}) — {s['note']}")
with tabs[2]:
    st.subheader('Interactive Climate Quiz')
    chosen=st.selectbox('Choose quiz topic',[l['title'] for l in LESSONS],key='quiz_choice')
    qlesson=next(x for x in LESSONS if x['title']==chosen)
    with st.form('quiz_form'):
        answers={}
        for q in qlesson['questions']:
            answers[q['id']]=st.radio(q['question'],q['options'],index=None,key='answer_'+q['id'])
        submitted=st.form_submit_button('Check answers',type='primary')
    if submitted:
        if any(v is None for v in answers.values()): st.warning('Answer every question before submitting.')
        else:
            result=grade(qlesson['questions'],answers)
            run_id=save_quiz(DB,qlesson['id'],result)
            st.session_state.quiz_results[qlesson['id']]=result
            st.success(f"Score: {result['correct']}/{result['total']} ({result['percentage']}%). Anonymous run #{run_id} saved.")
    if qlesson['id'] in st.session_state.quiz_results:
        for item in st.session_state.quiz_results[qlesson['id']]['details']:
            st.write(('✅' if item['is_correct'] else '🔎')+' '+item['question'])
            st.caption(f"Correct answer: {item['correct_answer']} · {item['feedback']}")
with tabs[3]:
    st.subheader('Youth Climate Action Lab')
    st.write('Explore practical actions. Points are an educational game score, not emissions reductions or measured environmental impact.')
    selected=st.multiselect('Choose actions',[a['title'] for a in ACTIONS])
    ids=[a['id'] for a in ACTIONS if a['title'] in selected]
    outcome=simulate_actions(ACTIONS,ids)
    st.metric('Illustrative learning points',outcome['learning_points'])
    st.write('**Topics explored:**',', '.join(outcome['categories']) if outcome['categories'] else 'Select an action')
    st.caption(outcome['note'])
    st.dataframe(pd.DataFrame(ACTIONS)[['title','category','description','points']],hide_index=True,use_container_width=True)
with tabs[4]:
    st.subheader('Gemini AI Learning Assistant')
    st.warning('AI-generated content is not independently verified. A reviewer must compare claims with the original sources.')
    topic=st.selectbox('Lesson for AI explanation',[l['title'] for l in LESSONS],key='ai_choice')
    current=next(x for x in LESSONS if x['title']==topic)
    st.write('**Selected references**')
    for s in SOURCES:
        if s['id'] in current['source_ids']:
            st.markdown(f"- [{s['title']}]({s['url']}) ({s['id']})")
    key=os.getenv('GEMINI_API_KEY','').strip()
    if st.button('Generate explanation with Gemini 2.5 Flash',type='primary'):
        if not key: st.error('Add GEMINI_API_KEY to your local .env file first.')
        else:
            try:
                with st.spinner('Requesting an educational explanation...'):
                    output=explain_with_gemini(current,SOURCES,key,os.getenv('GEMINI_MODEL','gemini-2.5-flash'))
                st.session_state.ai_output=output.model_dump()
                st.session_state.ai_lesson=current['id']
                st.success('API response received. Human review is required.')
            except Exception as e:
                st.error(f'AI request failed ({type(e).__name__}). Check model access, API key, network, and response format. Details: {str(e)[:300]}')
    if st.session_state.ai_output:
        st.json(st.session_state.ai_output)
        st.caption('Source IDs are checked against supplied material; this does not verify scientific correctness or quotation fidelity.')
        with st.form('review_form'):
            reviewer=st.text_input('Reviewer role or pseudonym',value='Educational Reviewer')
            decision=st.selectbox('Decision',['needs_revision','approved','rejected'])
            notes=st.text_area('Evidence review notes',value='Check the original source context and all claims before approval.')
            if st.form_submit_button('Save human review'):
                try:
                    review=Review(decision=decision,reviewer=reviewer,notes=notes)
                    record=save_review(DB,st.session_state.ai_lesson,review,st.session_state.ai_output)
                    st.success(f'Human review #{record} saved locally.')
                except Exception as e: st.error(str(e))
with tabs[5]:
    st.subheader('Learning Progress & Exports')
    quiz_data=records(DB,'quiz_runs'); review_data=records(DB,'ai_reviews')
    a,b=st.columns(2);a.metric('Anonymous quiz attempts',len(quiz_data));b.metric('Human AI reviews',len(review_data))
    st.write('**Anonymous quiz attempts**')
    st.dataframe(pd.DataFrame(quiz_data),use_container_width=True,hide_index=True)
    st.write('**Human review records**')
    st.dataframe(pd.DataFrame([{k:v for k,v in x.items() if k!='response_json'} for x in review_data]),use_container_width=True,hide_index=True)
    st.download_button('Download quiz history (CSV)',pd.DataFrame(quiz_data).to_csv(index=False).encode('utf-8'),'quiz_history.csv','text/csv')
    st.download_button('Download review history (CSV)',pd.DataFrame(review_data).to_csv(index=False).encode('utf-8'),'human_reviews.csv','text/csv')
    export={'content':CONTENT,'quiz_runs':quiz_data,'ai_reviews':review_data,'content_sha256':sha256(CONTENT),'limitations':['Synthetic learning points are not environmental impact estimates.','AI outputs require human review.','Reference excerpts include paraphrases and must be checked against original sources.','No learning outcomes have been scientifically evaluated.']}
    st.download_button('Download educational data and audit (JSON)',json.dumps(export,indent=2,ensure_ascii=False).encode('utf-8'),'climate_education_export.json','application/json')
    st.markdown('**Methodology and limitations**')
    for item in export['limitations']: st.write('- '+item)
    st.caption('Quiz results are stored anonymously in local SQLite. Reviewer pseudonyms are optional role labels, not student identities. Delete local_data/learning.sqlite3 to clear records.')
