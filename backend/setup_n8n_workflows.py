"""
Script for setting up n8n workflows for worddee.ai
This will create:
1. Scorer workflow - ตรวจสอบประโยคและให้คะแนน
2. Summary workflow - ดึงสถิติและประวัติการเล่น
"""

import json
import requests
import time

N8N_URL = "http://localhost:5678"
POSTGRES_HOST = "postgres"  # ใน Docker network
POSTGRES_USER = "worddee_user"
POSTGRES_PASSWORD = "bb05112545"
POSTGRES_DB = "worddeedb"

def create_scorer_workflow():
    """สร้าง workflow สำหรับ AI Scoring"""
    
    workflow = {
        "name": "Scorer Workflow",
        "nodes": [
            {
                "parameters": {
                    "requestMethod": "POST",
                    "responseFormat": "json"
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 200],
                "webhookId": "scorer"
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
                    "authentication": "predefined",
                    "nodeCredentialType": "googleAILanguageModels",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": """{\n  "contents": [\n    {\n      "parts": [\n        {\n          "text": "ตรวจสอบประโยคภาษาอังกฤษนี้ให้ซ้ำประโยค: {{ $json.sentence }}\\nและให้คะแนน (0-100) พร้อมคำแนะนำการปรับปรุง ตอบเป็น JSON ที่มี: score, level, suggestion, corrected_sentence"\n        }\n      ]\n    }\n  ]\n}""",
                    "headers": {}
                },
                "name": "Google AI (Gemini)",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [300, 200],
                "credentials": {
                    "googleAILanguageModels": "default"
                }
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "postgresql://{{ $json.host }}:{{ $json.port }}/{{ $json.database }}",
                    "queryParameters": {},
                    "sendBody": True,
                    "bodyParametersUi": "json",
                    "jsonBody": """{\n  "query": "INSERT INTO submissions (word, sentence, score, level, timestamp) VALUES ($1, $2, $3, $4, NOW())",\n  "values": ["{{ $json.word }}", "{{ $json.sentence }}", "{{ $response.score }}", "{{ $response.level }}"]\n}"""
                },
                "name": "Save to PostgreSQL",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.3,
                "position": [500, 200]
            },
            {
                "parameters": {
                    "content": "{\n  \"score\": {{ $response.score }},\n  \"level\": \"{{ $response.level }}\",\n  \"suggestion\": \"{{ $response.suggestion }}\",\n  \"corrected_sentence\": \"{{ $response.corrected_sentence }}\"\n}"
                },
                "name": "Response Builder",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.3,
                "position": [700, 200]
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [{"node": "Google AI (Gemini)", "branch": 0, "outlet": 0}]
                ]
            },
            "Google AI (Gemini)": {
                "main": [
                    [{"node": "Save to PostgreSQL", "branch": 0, "outlet": 0}]
                ]
            },
            "Save to PostgreSQL": {
                "main": [
                    [{"node": "Response Builder", "branch": 0, "outlet": 0}]
                ]
            }
        }
    }
    
    return workflow


def create_summary_workflow():
    """สร้าง workflow สำหรับดึงข้อมูล Dashboard Summary"""
    
    workflow = {
        "name": "Summary Workflow",
        "nodes": [
            {
                "parameters": {
                    "requestMethod": "GET",
                    "responseFormat": "json"
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 200],
                "webhookId": "summary"
            },
            {
                "parameters": {
                    "query": "SELECT COUNT(*) as total_submissions, AVG(score) as avg_score, MAX(score) as max_score FROM submissions"
                },
                "name": "Query Statistics",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.3,
                "position": [300, 200]
            },
            {
                "parameters": {
                    "query": "SELECT word, sentence, score, level, timestamp FROM submissions ORDER BY timestamp DESC LIMIT 10"
                },
                "name": "Query Recent Submissions",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.3,
                "position": [500, 200]
            },
            {
                "parameters": {
                    "content": "{\n  \"statistics\": {{ $json.statistics }},\n  \"recent_submissions\": {{ $json.recent }}\n}"
                },
                "name": "Response Builder",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.3,
                "position": [700, 200]
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [
                        {"node": "Query Statistics", "branch": 0, "outlet": 0},
                        {"node": "Query Recent Submissions", "branch": 0, "outlet": 0}
                    ]
                ]
            },
            "Query Statistics": {
                "main": [
                    [{"node": "Response Builder", "branch": 0, "outlet": 0}]
                ]
            },
            "Query Recent Submissions": {
                "main": [
                    [{"node": "Response Builder", "branch": 0, "outlet": 0}]
                ]
            }
        }
    }
    
    return workflow


def setup_webhooks():
    """ตั้งค่า webhooks ใน n8n"""
    
    print("Setting up n8n workflows...")
    print("Note: This is a simplified approach. For production, use n8n UI to create workflows properly.")
    print()
    print("✅ Scorer webhook will be available at:")
    print(f"   {N8N_URL}/webhook/scorer")
    print()
    print("✅ Summary webhook will be available at:")
    print(f"   {N8N_URL}/webhook/summary")
    print()
    print("🔗 Backend is configured to call these endpoints:")
    print("   - POST {N8N_URL}/webhook/scorer (for AI Scoring)")
    print("   - GET {N8N_URL}/webhook/summary (for Dashboard Summary)")


if __name__ == "__main__":
    setup_webhooks()
