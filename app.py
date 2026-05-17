from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, List

from flask import Flask, jsonify, redirect, render_template_string, request, send_from_directory, url_for


try:
    from dotenv import load_dotenv
except ImportError:  # Keeps the app running even before requirements are installed.
    def load_dotenv():
        return None

try:
    from openai import OpenAI
except ImportError:  # Keeps non-AI routes working if OpenAI package is missing.
    OpenAI = None

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

PROFILE = {
    "name": "Pravav Pardhi",
    "brand": "Pravav.AI Studio",
    "role": "AI, Data Analytics & Automation Freelancer",
    "tagline": "I build AI-powered business systems, live dashboards, NLP tools, and automation workflows that turn raw data into decisions.",
    "email": "your-email@example.com",
    "phone": "+91 7489636232",
    "location": "India",
    "linkedin": "https://www.linkedin.com/in/pranav-pardhi-568726236/",
    "github": "https://github.com/pranav10pardhi",
    "resume_file": "resume.pdf",
}

SERVICES = [
    {"icon": "🤖", "title": "Custom AI Chatbots", "description": "Website assistants, FAQ bots, document Q&A, support bots, and lead qualification assistants.", "points": ["FAQ automation", "Lead capture", "Document Q&A", "Internal knowledge bot"]},
    {"icon": "📊", "title": "Live Dashboards", "description": "Executive dashboards for sales, finance, HR, operations, and customer insights.", "points": ["KPI design", "Power BI / Streamlit", "Interactive charts", "Business reporting"]},
    {"icon": "📈", "title": "Business Data Analysis", "description": "Data cleaning, SQL analysis, Excel automation, insight reports, and decision-ready analytics.", "points": ["Python + Pandas", "SQL reporting", "Data quality", "Monthly insights"]},
    {"icon": "🧠", "title": "NLP & LLM Apps", "description": "Text classification, sentiment analysis, summarization, resume parsing, and LLM prototypes.", "points": ["Prompt engineering", "Text intelligence", "RAG-ready design", "AI prototypes"]},
]

CASE_STUDIES = [
    {"title": "Sales Intelligence Dashboard", "industry": "Retail / E-commerce", "problem": "Sales data was scattered across Excel sheets, making revenue trends, customer behavior, and product performance difficult to track.", "solution": "Created a KPI dashboard with monthly revenue, top products, region performance, conversion indicators, and reporting automation logic.", "impact": "Reduced manual reporting effort and gave founders a single decision-ready business view.", "stack": ["Python", "Pandas", "SQL", "Dashboard UI", "KPI Design"]},
    {"title": "AI Knowledge Assistant", "industry": "Service / Consulting", "problem": "Teams repeatedly answered the same service, pricing, document, and process questions manually.", "solution": "Designed a chatbot workflow that answers FAQs, collects leads, summarizes requirements, and guides visitors to the right service.", "impact": "Improved response speed, lead qualification, and customer experience.", "stack": ["Flask", "LLM Workflow", "Prompt Engineering", "NLP", "Automation"]},
]

TESTIMONIALS: List[Dict[str, str]] = [
    {"name": "Demo Client", "role": "Founder, Retail Startup", "message": "The dashboard and automation concept looks client-ready, clean, and business-focused.", "time": "Sample testimonial"},
    {"name": "Operations Manager", "role": "Service Business", "message": "The AI assistant demo clearly explains how reports, customer questions, and business data can be handled faster.", "time": "Sample testimonial"},
    {"name": "Analytics Lead", "role": "Data Team", "message": "Strong visual presentation with practical AI use cases and dashboard storytelling.", "time": "Sample testimonial"},
]

DASHBOARDS = [
    {"id": "revenueChart", "title": "Revenue Performance Dashboard", "summary": "Sales analytics for monthly revenue, orders, conversion rate, and channel performance.", "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"], "data": [180, 230, 270, 310, 390, 460, 530], "metrics": [{"label": "Revenue", "value": "₹12.8L", "change": "+18%"}, {"label": "Orders", "value": "1,284", "change": "+11%"}, {"label": "Conversion", "value": "7.4%", "change": "+2.1%"}, {"label": "Avg. Order", "value": "₹997", "change": "+8%"}]},
    {"id": "automationChart", "title": "Automation Impact Dashboard", "summary": "Workflow analytics for time saved, data quality, automation coverage, and support response speed.", "labels": ["Manual", "Cleaned", "Automated", "Reported", "Reviewed"], "data": [92, 76, 52, 34, 18], "metrics": [{"label": "Hours Saved", "value": "48 hrs", "change": "+32%"}, {"label": "Data Quality", "value": "96%", "change": "+14%"}, {"label": "Tasks Automated", "value": "22", "change": "+9"}, {"label": "Response Speed", "value": "3.2x", "change": "faster"}]},
]

CHATBOT_KNOWLEDGE = {
    "dashboard": "I can build sales, finance, HR, operations, and executive KPI dashboards using Python, SQL, Power BI, Streamlit, or custom web dashboards.",
    "chatbot": "I can create AI chatbots for FAQs, lead collection, internal knowledge, document Q&A, and support automation.",
    "automation": "I can automate repetitive Excel, CSV, API, email, and reporting workflows using Python and cloud tools.",
    "nlp": "I can build NLP projects such as sentiment analysis, resume parsing, summarization, classification, and document intelligence.",
    "price": "Project pricing depends on scope, data sources, integrations, and deployment needs. Share your requirements and I can suggest a practical plan.",
    "contact": f"You can contact {PROFILE['name']} at {PROFILE['email']} or through LinkedIn/GitHub links on this website.",
}

HTML = r'''
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{{ profile.name }} | AI, Data & Automation Portfolio</title><meta name="description" content="Professional AI, Data Analytics, Dashboard, NLP, LLM and Automation freelancer portfolio."><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet"><script src="https://cdn.jsdelivr.net/npm/chart.js" defer></script>
<style>:root{--bg:#050714;--bg2:#071023;--panel:rgba(255,255,255,.075);--border:rgba(255,255,255,.14);--text:#fff;--muted:#aebad6;--cyan:#39d5ff;--blue:#5d7cff;--violet:#a855f7;--green:#36f6a6;--shadow:0 30px 90px rgba(0,0,0,.36)}*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--text);line-height:1.65;overflow-x:hidden}a{text-decoration:none;color:inherit}.container{width:min(92%,1220px);margin:auto}.section{padding:110px 0;position:relative}.site-header{position:sticky;top:0;z-index:50;background:rgba(5,7,20,.72);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}.nav{min-height:76px;display:flex;align-items:center;justify-content:space-between}.logo{font-family:'Space Grotesk';font-size:1.35rem;font-weight:800}.logo span{color:var(--cyan)}.nav-links{display:flex;gap:24px;align-items:center}.nav-links a{color:#dbe5ff;opacity:.82}.nav-links a:hover{color:var(--cyan);opacity:1}.menu-toggle{display:none;background:transparent;color:white;border:0;font-size:1.7rem}.btn-primary,.btn-secondary,.nav-btn{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;font-weight:900;transition:.28s ease}.btn-primary,.nav-btn{background:linear-gradient(135deg,var(--cyan),var(--blue),var(--violet));padding:14px 22px;box-shadow:0 20px 55px rgba(93,124,255,.26);border:0;color:white;cursor:pointer}.btn-secondary{padding:13px 21px;background:rgba(255,255,255,.07);border:1px solid var(--border)}.btn-primary:hover,.btn-secondary:hover,.nav-btn:hover{transform:translateY(-4px)}#particleCanvas{position:fixed;inset:0;z-index:-3}.cursor-glow{position:fixed;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(57,213,255,.13),transparent 70%);pointer-events:none;z-index:-1;transform:translate(-50%,-50%)}.hero{min-height:92vh;display:flex;align-items:center;overflow:hidden}.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:60px;align-items:center}.eyebrow{display:inline-flex;gap:10px;align-items:center;padding:9px 15px;border-radius:999px;border:1px solid rgba(57,213,255,.3);background:rgba(57,213,255,.08);color:#b9f4ff;font-weight:800;margin-bottom:20px}.eyebrow span,.status-dot{width:10px;height:10px;border-radius:50%;background:var(--green);box-shadow:0 0 0 0 rgba(54,246,166,.65);animation:pulse 1.7s infinite}.hero h1{font-family:'Space Grotesk';font-size:clamp(2.7rem,7vw,6.4rem);line-height:.96;letter-spacing:-.06em;margin-bottom:24px}.hero h1 b{background:linear-gradient(120deg,#fff,var(--cyan),#b6b9ff,var(--violet));background-size:260% 260%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientMove 5s ease infinite}.hero p{font-size:1.08rem;color:var(--muted);max-width:760px;margin-bottom:30px}.hero-actions{display:flex;gap:14px;flex-wrap:wrap}.hero-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:42px}.hero-stats div,.metric{padding:20px;border-radius:22px;background:var(--panel);border:1px solid var(--border)}.hero-stats strong,.metric strong{display:block;font-family:'Space Grotesk';font-size:1.8rem}.hero-stats span,.metric small,.metric span{color:var(--muted)}.hero-visual{position:relative;min-height:560px}.hologram-card{position:absolute;inset:48px 60px;border:1px solid var(--border);border-radius:36px;background:linear-gradient(180deg,rgba(255,255,255,.13),rgba(255,255,255,.045));box-shadow:var(--shadow);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;overflow:hidden}.hologram-card:before{content:"";position:absolute;inset:-40%;background:conic-gradient(transparent,rgba(57,213,255,.18),transparent,rgba(168,85,247,.2),transparent);animation:rotate 15s linear infinite}.hologram-card>*{position:relative}.scan-line{position:absolute;left:0;right:0;height:90px;background:linear-gradient(transparent,rgba(57,213,255,.18),transparent);animation:scan 3.5s ease-in-out infinite}.avatar-ring{width:190px;height:190px;padding:8px;border-radius:50%;background:linear-gradient(135deg,var(--cyan),var(--blue),var(--violet));margin-bottom:24px;animation:float 4s ease-in-out infinite}.avatar-ring .avatar{width:100%;height:100%;border-radius:50%;display:grid;place-items:center;background:#071023;font-size:4rem}.skill-pills{display:flex;gap:9px;flex-wrap:wrap;justify-content:center;margin-top:16px}.skill-pills span,.stack span{font-size:.82rem;padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.09);border:1px solid var(--border);color:#e7eeff}.float-chip{position:absolute;padding:13px 16px;border-radius:999px;background:rgba(5,7,20,.76);border:1px solid var(--border);backdrop-filter:blur(16px);box-shadow:var(--shadow);animation:float 4.2s ease-in-out infinite}.fc1{top:30px;left:0}.fc2{right:0;top:190px;animation-delay:-1.4s}.fc3{left:45px;bottom:54px;animation-delay:-2.2s}.aurora{position:absolute;border-radius:50%;filter:blur(20px);opacity:.36}.a1{width:420px;height:420px;background:var(--cyan);top:10%;left:-12%;animation:morph 10s infinite}.a2{width:520px;height:520px;background:var(--violet);right:-12%;bottom:10%;animation:morph 12s infinite reverse}.orbit{position:absolute;border:1px dashed rgba(255,255,255,.14);border-radius:50%;animation:rotate 30s linear infinite}.orbit-one{width:760px;height:760px;right:-240px;top:80px}.orbit-two{width:430px;height:430px;right:80px;top:230px;animation-direction:reverse}.section-title{text-align:center;max-width:820px;margin:0 auto 54px}.section-title span,.mini-label{color:var(--cyan);font-weight:900;text-transform:uppercase;letter-spacing:.14em;font-size:.8rem}.section-title h2,.text-block h2,.contact-card h2{font-family:'Space Grotesk';font-size:clamp(2rem,4.5vw,4rem);line-height:1.05;margin:12px 0 14px;letter-spacing:-.04em}.section-title p,.text-block p,.contact-card p{color:var(--muted)}.cards-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:22px}.service-card,.dashboard-card,.case-card,.testimonial,.contact-card,.chat-window{background:linear-gradient(180deg,rgba(255,255,255,.1),rgba(255,255,255,.04));border:1px solid var(--border);border-radius:30px;box-shadow:var(--shadow)}.service-card{min-height:340px;padding:26px;position:relative;overflow:hidden}.service-card:after{content:"";position:absolute;inset:auto -30% -45% -30%;height:160px;background:radial-gradient(circle,rgba(57,213,255,.22),transparent 70%);transition:.4s}.service-card:hover:after{transform:translateY(-40px)}.icon{font-size:2rem;width:64px;height:64px;display:grid;place-items:center;border-radius:20px;background:linear-gradient(135deg,var(--cyan),var(--blue),var(--violet));margin-bottom:18px}.service-card h3{font-family:'Space Grotesk';font-size:1.3rem;margin-bottom:10px}.service-card p,.service-card li{color:var(--muted);font-size:.94rem}.service-card ul{list-style:none;margin-top:16px}.service-card li:before{content:"✦ ";color:var(--green)}.dark-band{background:linear-gradient(180deg,rgba(255,255,255,.025),rgba(255,255,255,.06),rgba(255,255,255,.025))}.dashboard-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:28px}.dashboard-card{padding:26px}.dashboard-head{display:flex;justify-content:space-between;gap:18px}.dashboard-head h3{font-family:'Space Grotesk';font-size:1.5rem}.dashboard-head p{color:var(--muted);margin-top:8px}.live-badge{height:max-content;padding:7px 10px;border-radius:999px;background:rgba(54,246,166,.12);border:1px solid rgba(54,246,166,.3);color:#b9ffdf;font-size:.78rem;font-weight:900}.metrics-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.metric{padding:14px;border-radius:18px}.metric strong{font-size:1.25rem}.chart-wrap{height:270px;padding:18px;border-radius:22px;background:rgba(5,7,20,.45);border:1px solid rgba(255,255,255,.09)}.chatbot-grid{display:grid;grid-template-columns:.85fr 1.15fr;gap:38px;align-items:center}.feature-list{margin-top:18px;list-style:none}.feature-list li{margin-bottom:10px;color:#dce6ff}.feature-list li:before{content:"✓ ";color:var(--green)}code{background:rgba(255,255,255,.1);padding:3px 6px;border-radius:7px}.chat-window{overflow:hidden}.chat-header{padding:18px 22px;border-bottom:1px solid var(--border);display:flex;gap:12px;align-items:center}.chat-body{height:360px;overflow-y:auto;padding:22px}.message{max-width:84%;padding:13px 15px;border-radius:18px;margin-bottom:13px;animation:pop .28s ease}.message.bot{background:rgba(57,213,255,.12);border:1px solid rgba(57,213,255,.22)}.message.user{background:rgba(255,255,255,.09);border:1px solid var(--border);margin-left:auto}.chat-input{display:flex;gap:10px;padding:18px;border-top:1px solid var(--border)}input,textarea{width:100%;border:1px solid var(--border);background:rgba(255,255,255,.06);color:#fff;border-radius:16px;padding:14px 15px;outline:0;font-family:inherit}textarea{min-height:110px;resize:vertical}.case-grid{display:grid;gap:24px}.case-card{padding:28px}.case-top span{color:var(--cyan);font-weight:900}.case-top h3{font-family:'Space Grotesk';font-size:1.8rem;margin:6px 0 22px}.case-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.case-cols p{color:var(--muted);margin-top:6px}.stack{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}.testimonial-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.testimonial{padding:24px}.testimonial p{color:#e7eeff;margin-bottom:18px}.testimonial strong{display:block;color:var(--cyan)}.testimonial small{color:var(--muted)}.testimonial-form{margin:34px auto 0;max-width:820px;display:grid;grid-template-columns:1fr 1fr;gap:12px}.testimonial-form textarea{grid-column:span 2}.testimonial-form button{width:max-content}.contact-card{text-align:center;padding:58px}.contact-actions{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;margin:26px 0}.contact-meta{display:flex;gap:18px;flex-wrap:wrap;justify-content:center;color:var(--muted)}footer{padding:34px 0;text-align:center;color:var(--muted);border-top:1px solid var(--border)}.reveal{opacity:0;transform:translateY(36px);transition:opacity .75s ease,transform .75s ease}.reveal.visible{opacity:1;transform:translateY(0)}.error-box{margin:40px auto;max-width:900px;padding:24px;border:1px solid #ffaaaa55;border-radius:20px;background:#ff000011}@keyframes pulse{70%{box-shadow:0 0 0 12px rgba(54,246,166,0)}}@keyframes gradientMove{50%{background-position:100% 50%}}@keyframes rotate{to{transform:rotate(360deg)}}@keyframes scan{0%,100%{top:-20%}50%{top:100%}}@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-18px)}}@keyframes morph{50%{transform:translate(45px,-35px) scale(1.1);border-radius:38% 62% 70% 30%}}@keyframes pop{from{opacity:0;transform:scale(.96) translateY(8px)}to{opacity:1;transform:scale(1) translateY(0)}}@media(max-width:1050px){.cards-grid{grid-template-columns:repeat(2,1fr)}.hero-grid,.chatbot-grid,.dashboard-grid{grid-template-columns:1fr}.hero-visual{min-height:470px}.case-cols,.testimonial-grid{grid-template-columns:1fr}.metrics-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:720px){.nav-links{display:none;position:absolute;top:76px;left:0;right:0;background:rgba(5,7,20,.95);padding:18px;flex-direction:column}.nav-links.open{display:flex}.menu-toggle{display:block}.cards-grid,.hero-stats{grid-template-columns:1fr}.hero-visual{display:none}.section{padding:82px 0}.testimonial-form{grid-template-columns:1fr}.testimonial-form textarea{grid-column:auto}.chart-wrap{height:230px}}</style></head>
<body><canvas id="particleCanvas"></canvas><div class="cursor-glow"></div><header class="site-header"><div class="container nav"><a href="#home" class="logo">{{ profile.brand }}<span>.</span></a><button class="menu-toggle" type="button">☰</button><nav class="nav-links"><a href="#services">Services</a><a href="#dashboards">Dashboards</a><a href="#chatbot">Chatbot</a><a href="#cases">Case Studies</a><a href="#testimonials">Testimonials</a><a href="#contact" class="nav-btn">Start Project</a></nav></div></header><main><section id="home" class="hero"><div class="aurora a1"></div><div class="aurora a2"></div><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="container hero-grid"><div class="reveal"><div class="eyebrow"><span></span> AI • Data • Dashboards • Automation</div><h1>Build <b>AI-powered business systems</b> that clients remember.</h1><p>{{ profile.tagline }}</p><div class="hero-actions"><a href="#services" class="btn-primary">Explore Services</a><a href="#dashboards" class="btn-secondary">View Dashboards</a></div><div class="hero-stats"><div><strong>2</strong><span>Live dashboard demos</span></div><div><strong>1</strong><span>AI chatbot demo</span></div><div><strong>2+</strong><span>Professional case studies</span></div></div></div><div class="hero-visual reveal"><div class="float-chip fc1">⚡ Automation Ready</div><div class="float-chip fc2">📊 KPI Dashboards</div><div class="float-chip fc3">🤖 AI Assistant</div><div class="hologram-card tilt"><div class="scan-line"></div><div class="avatar-ring"><div class="avatar">👨‍💻</div></div><h2>{{ profile.name }}</h2><p>{{ profile.role }}</p><div class="skill-pills"><span>Python</span><span>SQL</span><span>AI</span><span>Dashboards</span></div></div></div></div></section><section id="services" class="section"><div class="container"><div class="section-title reveal"><span>Services</span><h2>Client-ready solutions, not just code.</h2><p>Every section is designed to present your freelancing work professionally and convert visitors into leads.</p></div><div class="cards-grid">{% for service in services %}<article class="service-card reveal tilt"><div class="icon">{{ service.icon }}</div><h3>{{ service.title }}</h3><p>{{ service.description }}</p><ul>{% for point in service.points %}<li>{{ point }}</li>{% endfor %}</ul></article>{% endfor %}</div></div></section><section id="dashboards" class="section dark-band"><div class="container"><div class="section-title reveal"><span>Live Dashboard Demos</span><h2>Two impressive dashboard showcases.</h2><p>Charts are animated using Chart.js and can later connect to real APIs, SQL, CSV, Power BI, or Streamlit.</p></div><div class="dashboard-grid">{% for dashboard in dashboards %}<article class="dashboard-card reveal"><div class="dashboard-head"><div><h3>{{ dashboard.title }}</h3><p>{{ dashboard.summary }}</p></div><span class="live-badge">Live Demo</span></div><div class="metrics-grid">{% for metric in dashboard.metrics %}<div class="metric"><small>{{ metric.label }}</small><strong>{{ metric.value }}</strong><span>{{ metric.change }}</span></div>{% endfor %}</div><div class="chart-wrap"><canvas id="{{ dashboard.id }}" data-labels='{{ dashboard.labels|tojson }}' data-values='{{ dashboard.data|tojson }}'></canvas></div></article>{% endfor %}</div></div></section><section id="chatbot" class="section"><div class="container chatbot-grid"><div class="text-block reveal"><span class="mini-label">AI Chatbot Demo</span><h2>A portfolio assistant that talks about your services.</h2><p>This demo uses a safe local Flask API route. Later, you can connect OpenAI, Gemini, LangChain, or a document-based RAG system.</p><ul class="feature-list"><li>Ask: <code>dashboard</code></li><li>Ask: <code>chatbot</code></li><li>Ask: <code>automation</code></li><li>Ask: <code>price</code></li></ul></div><div class="chat-window reveal"><div class="chat-header"><span class="status-dot"></span><strong>Pravav.AI Assistant</strong></div><div class="chat-body" id="chatBody"><div class="message bot">Hello! Ask me about dashboards, AI chatbots, automation, NLP, pricing, or contact details.</div></div><form class="chat-input" id="chatForm"><input id="chatInput" type="text" placeholder="Type your question..." autocomplete="off"><button class="btn-primary" type="submit">Send</button></form></div></div></section><section id="cases" class="section"><div class="container"><div class="section-title reveal"><span>Case Studies</span><h2>Show clients the business impact.</h2></div><div class="case-grid">{% for case in case_studies %}<article class="case-card reveal"><div class="case-top"><span>{{ case.industry }}</span><h3>{{ case.title }}</h3></div><div class="case-cols"><div><b>Problem</b><p>{{ case.problem }}</p></div><div><b>Solution</b><p>{{ case.solution }}</p></div><div><b>Impact</b><p>{{ case.impact }}</p></div></div><div class="stack">{% for item in case.stack %}<span>{{ item }}</span>{% endfor %}</div></article>{% endfor %}</div></div></section><section id="testimonials" class="section dark-band"><div class="container"><div class="section-title reveal"><span>Client Testimonials</span><h2>Social proof that feels trustworthy.</h2></div><div class="testimonial-grid">{% for item in testimonials %}<article class="testimonial reveal"><p>“{{ item.message }}”</p><strong>{{ item.name }}</strong><small>{{ item.role }} • {{ item.time }}</small></article>{% endfor %}</div><form class="testimonial-form reveal" method="POST" action="/comment"><input name="name" placeholder="Client name" required><input name="role" placeholder="Role / Company"><textarea name="message" placeholder="Client testimonial or feedback" required></textarea><button class="btn-primary" type="submit">Add Testimonial</button></form></div></section><section id="contact" class="section contact-section"><div class="container contact-card reveal"><h2>Ready to launch a professional AI/Data project?</h2><p>Connect on LinkedIn, explore GitHub projects, download the resume, or send a project email.</p><div class="contact-actions"><a class="btn-primary" href="mailto:{{ profile.email }}">Email Me</a><a class="btn-secondary" href="{{ profile.linkedin }}" target="_blank" rel="noreferrer">LinkedIn</a><a class="btn-secondary" href="{{ profile.github }}" target="_blank" rel="noreferrer">GitHub</a><a class="btn-secondary" href="/resume">Resume</a></div><div class="contact-meta"><span>{{ profile.phone }}</span><span>{{ profile.location }}</span><span>{{ profile.email }}</span></div></div></section></main><footer><div class="container">© {{ year }} {{ profile.name }}. Built with Flask, motion graphics, dashboards and AI chatbot demo.</div></footer>
<script>document.addEventListener('DOMContentLoaded',()=>{const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);const cursor=$('.cursor-glow');document.addEventListener('mousemove',e=>{if(cursor){cursor.style.left=e.clientX+'px';cursor.style.top=e.clientY+'px';}});$('.menu-toggle')?.addEventListener('click',()=>$('.nav-links')?.classList.toggle('open'));const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target)}}),{threshold:.14});$$('.reveal').forEach(el=>io.observe(el));$$('.tilt').forEach(card=>{card.addEventListener('mousemove',e=>{const r=card.getBoundingClientRect();const x=(e.clientX-r.left)/r.width-.5;const y=(e.clientY-r.top)/r.height-.5;card.style.transform=`perspective(900px) rotateX(${y*-7}deg) rotateY(${x*7}deg) translateY(-4px)`});card.addEventListener('mouseleave',()=>card.style.transform='')});const canvas=$('#particleCanvas'),ctx=canvas?.getContext('2d');let pts=[];function resize(){if(!canvas)return;canvas.width=innerWidth;canvas.height=innerHeight;pts=Array.from({length:Math.min(80,Math.floor(innerWidth/18))},()=>({x:Math.random()*canvas.width,y:Math.random()*canvas.height,vx:(Math.random()-.5)*.45,vy:(Math.random()-.5)*.45}))}function draw(){if(!ctx)return;ctx.clearRect(0,0,canvas.width,canvas.height);pts.forEach((p,i)=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>canvas.width)p.vx*=-1;if(p.y<0||p.y>canvas.height)p.vy*=-1;ctx.beginPath();ctx.arc(p.x,p.y,1.6,0,Math.PI*2);ctx.fillStyle='rgba(57,213,255,.55)';ctx.fill();for(let j=i+1;j<pts.length;j++){const q=pts[j],d=Math.hypot(p.x-q.x,p.y-q.y);if(d<120){ctx.strokeStyle=`rgba(93,124,255,${(1-d/120)*.22})`;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();}}});requestAnimationFrame(draw)}resize();draw();addEventListener('resize',resize);function makeChart(el,type='line'){if(!el||!window.Chart)return;const labels=JSON.parse(el.dataset.labels||'[]'),data=JSON.parse(el.dataset.values||'[]');new Chart(el,{type, data:{labels,datasets:[{label:'Performance',data,borderWidth:3,tension:.42,fill:true}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#aebad6'},grid:{color:'rgba(255,255,255,.06)'}},y:{ticks:{color:'#aebad6'},grid:{color:'rgba(255,255,255,.06)'}}}}})}makeChart($('#revenueChart'),'line');makeChart($('#automationChart'),'bar');const form=$('#chatForm'),input=$('#chatInput'),body=$('#chatBody');function addMsg(text,cls){const div=document.createElement('div');div.className='message '+cls;div.textContent=text;body.appendChild(div);body.scrollTop=body.scrollHeight}form?.addEventListener('submit',async e=>{e.preventDefault();const msg=input.value.trim();if(!msg)return;addMsg(msg,'user');input.value='';addMsg('Typing...','bot');try{const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});const data=await res.json();body.lastChild.textContent=data.reply||'I can help with AI, dashboards and automation.'}catch(err){body.lastChild.textContent='Chat demo is temporarily unavailable, but the website is working.'}})});</script></body></html>
'''


def get_openai_client():
    """Create OpenAI client only when the API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key)


def build_portfolio_prompt() -> str:
    """System prompt that turns the website chatbot into a professional lead assistant."""
    services = ", ".join(service["title"] for service in SERVICES)
    case_titles = "; ".join(case["title"] for case in CASE_STUDIES)
    return f"""
You are a professional AI chatbot for {PROFILE['name']}'s portfolio website.

Business profile:
- Name: {PROFILE['name']}
- Brand: {PROFILE['brand']}
- Role: {PROFILE['role']}
- Email: {PROFILE['email']}
- Phone: {PROFILE['phone']}
- Location: {PROFILE['location']}
- LinkedIn: {PROFILE['linkedin']}
- GitHub: {PROFILE['github']}

Services offered:
{services}

Portfolio case studies:
{case_titles}

Your goals:
1. Explain services clearly to website visitors.
2. Recommend a practical solution based on the visitor's problem.
3. Collect requirements naturally: business type, service needed, data source, features, deadline, and budget range.
4. Convert serious visitors into leads by suggesting they contact Pravav.

Rules:
- Be warm, professional, confident, and concise.
- Keep replies under 120 words unless the user asks for detail.
- Ask only one follow-up question at the end.
- If the user asks pricing, say it depends on scope, integrations, data source, timeline, and deployment.
- Do not invent exact prices, delivery dates, or fake completed client work.
- If the user wants contact details, share email, phone, LinkedIn, and GitHub.
- If the user is confused, suggest 2 or 3 clear service options.
""".strip()


def local_chatbot_fallback(user_message: str) -> str:
    """Helpful fallback when OPENAI_API_KEY is not configured or API is unavailable."""
    message = user_message.lower()
    if any(word in message for word in ["dashboard", "report", "power bi", "kpi", "analytics"]):
        return "I can help with sales, HR, finance, operations, and executive dashboards. Please share your data source, required KPIs, and whether you want Power BI, Streamlit, or a web dashboard."
    if any(word in message for word in ["chatbot", "bot", "ai assistant", "faq"]):
        return "I can help build a real AI chatbot for FAQs, lead capture, company knowledge, document Q&A, and website support. Should your chatbot answer from fixed FAQs or from uploaded company documents?"
    if any(word in message for word in ["automation", "excel", "manual", "api", "workflow"]):
        return "I can automate Excel reports, CSV cleaning, API workflows, email reporting, and repetitive business tasks using Python. Which manual task do you want to automate first?"
    if any(word in message for word in ["price", "cost", "budget", "charges"]):
        return "Pricing depends on project scope, data source, integrations, timeline, and deployment. Share the service you need, required features, and budget range so I can suggest a practical plan."
    if any(word in message for word in ["contact", "email", "phone", "call", "linkedin"]):
        return f"You can contact {PROFILE['name']} at {PROFILE['email']} or {PROFILE['phone']}. LinkedIn: {PROFILE['linkedin']} GitHub: {PROFILE['github']}"
    return "I can help with AI chatbots, dashboards, data analysis, NLP, LLM apps, and Python automation. What business problem do you want to solve?"


@app.route("/")
def home():
    return render_template_string(
        HTML,
        profile=PROFILE,
        services=SERVICES,
        case_studies=CASE_STUDIES,
        testimonials=TESTIMONIALS,
        dashboards=DASHBOARDS,
        year=datetime.now().year,
    )

@app.route("/comment", methods=["POST"])
def add_comment():
    name = request.form.get("name", "").strip()[:80]
    role = (request.form.get("role", "Visitor").strip() or "Visitor")[:100]
    message = request.form.get("message", "").strip()[:500]
    if name and message:
        TESTIMONIALS.insert(0, {"name": name, "role": role, "message": message, "time": datetime.now().strftime("%d %b %Y, %I:%M %p")})
    return redirect(url_for("home") + "#testimonials")

@app.route("/api/chat", methods=["POST"])
def ai_chatbot_demo():
    """Real AI chatbot endpoint using OpenAI, with safe fallback handling."""
    payload = request.get_json(silent=True) or {}
    user_message = str(payload.get("message", "")).strip()[:1200]

    if not user_message:
        return jsonify({
            "reply": "Hi! I am Pravav's AI assistant. Ask me about dashboards, AI chatbots, automation, NLP, pricing, or project planning.",
            "mode": "empty_message",
        })

    client = get_openai_client()
    if client is None:
        return jsonify({
            "reply": local_chatbot_fallback(user_message) + "\n\nNote: Real AI mode will activate after adding OPENAI_API_KEY in environment variables.",
            "mode": "fallback_no_api_key",
        })

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=[
                {"role": "system", "content": build_portfolio_prompt()},
                {"role": "user", "content": user_message},
            ],
            max_output_tokens=300,
            temperature=0.5,
        )

        reply = getattr(response, "output_text", "") or local_chatbot_fallback(user_message)
        return jsonify({"reply": reply, "mode": "openai"})

    except Exception as exc:
        app.logger.exception("AI chatbot error: %s", exc)
        return jsonify({
            "reply": local_chatbot_fallback(user_message) + "\n\nThe AI service is temporarily unavailable, but this fallback assistant can still guide you.",
            "mode": "fallback_api_error",
        })

@app.route("/resume")
def resume():
    resume_path = os.path.join(app.root_path, "static", PROFILE["resume_file"])
    if os.path.exists(resume_path):
        return send_from_directory("static", PROFILE["resume_file"], as_attachment=True)
    return "Resume file not uploaded yet. Add static/resume.pdf to enable download.", 404

@app.route("/health")
def health_check():
    return {"status": "ok", "service": "fixed-creative-ai-data-portfolio"}, 200

@app.errorhandler(404)
def not_found(_error):
    return redirect(url_for("home"))

@app.errorhandler(500)
def server_error(_error):
    return "A server error occurred. Check terminal logs. This fixed version avoids missing-template errors.", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
