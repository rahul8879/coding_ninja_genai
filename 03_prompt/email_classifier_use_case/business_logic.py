import json
from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv()


client = OpenAI()

def call_llm(prompt):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()



def load_prompt(filename):
    path = os.path.join('prompt', filename)
    with open(path, 'r') as f:
        return f.read()


def classify_with_cot(subject,body,sender):
    template = load_prompt('classify_cot.md')
    prompt = template.format(subject=subject, sender=sender, body=body)
    result = call_llm(prompt)

    # extration logic to get category and urgency
    catgeory, urgency = None, None
    for line in result.split('\n'):
        if 'CATEGORY' in line:
            category = line.split(':')[1].strip()
        if 'URGENCY' in line:
            urgency = line.split(':')[1].strip()
    
    return {
        'category': category,
        'urgency': urgency,
        'full_output': result
    }


from collections import Counter
def classify_with_self_consistency(email, n_runs=5):
    template = load_prompt("classify_cot.md")
    results  = []
    traces   = []

    for i in range(n_runs):
        prompt = template.format(
            subject=email["subject"],
            body   =email["body"],
            sender =email["sender"]
        )
        result = call_llm(prompt)
        traces.append(result)

        for line in result.split("\n"):
            if "CATEGORY:" in line:
                results.append(line.replace("CATEGORY:", "").strip())
    votes = Counter(results)
    winner = votes.most_common(1)[0]
    confidence = winner[1] / n_runs *100
    urgency = None
    for line in traces[0].split("\n"):      
          if "URGENCY:" in line:
            urgency = line.replace("URGENCY:", "").strip()
    return {
        "category": winner[0],
        "urgency": urgency,
        "confidence": confidence,
    }

        
        
def draft_response_with_tot(email, classification):
    template = load_prompt("tree_of_thought.md")
    prompt   = template.format(
        subject =email["subject"],
        body    =email["body"],
        category=classification["category"]
    )
    return call_llm(prompt)