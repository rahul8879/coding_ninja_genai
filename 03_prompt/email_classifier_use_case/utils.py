# util function
from email_classifier_use_case.business_logic import classify_with_cot,  classify_with_self_consistency, call_llm, load_prompt,draft_response_with_tot

def is_enterprise_customer(sender):
    enterprise_domains = ["bigclient.com", "enterprise.com", "corp.com"]
    domain = sender.split("@")[-1] if "@" in sender else ""
    return domain in enterprise_domains


def process_email(email):
    # Step 1: Classify the email using CoT
    intial = classify_with_cot(email['subject'], email['body'], email['sender'])
    
    # step 2 : check for high stakes customers
    is_high_stakes = is_enterprise_customer(email['sender'])
    print(f"Is high stakes customer: {is_high_stakes}")

    # step 3 : if high stakes then use self consistency else use cot
    if is_high_stakes:
        final = classify_with_self_consistency(email,3)
    else:
        final = intial

    # step $ routing
    routing = {
        "Billing"        : "billing-team@company.com",
        "Technical"      : "tech-support@company.com",
        "Feature Request": "product@company.com",
        "Spam"           : None,
    }
    routed_to = routing.get(final['category'], "support@company.com")
    # step 5 : ToT for churn risk ( this need to improve?? how ??) # Assignment : try to call llm here 
    is_churn_risk = (
        "cancel" in email['body'].lower()
        or "not satisfied" in email['body'].lower()
        or "bad experience" in email['body'].lower()
    )

    drafted_response = None
    if is_churn_risk:
        drafted_response = draft_response_with_tot(email,final)


    return {
        "email_id"          : email.get("id", "N/A"),
        "classification"    : final,
        "routed_to"         : routed_to,
        "drafted_response"  : drafted_response,
        "needs_human_review": final.get("needs_human_review", False),
        "audit_trail"       : final.get("reasoning_traces", [])
    }


