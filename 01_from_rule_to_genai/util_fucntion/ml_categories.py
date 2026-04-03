"""
ML Categories Teaching Flow
From KNN → Supervised vs Unsupervised

Teaching Strategy:
1. Build on what they know (KNN)
2. Show the difference visually
3. Give real banking examples
4. Interactive comparison
"""

# ============================================
# PART 1: What They Already Know
# ============================================

print("=" * 60)
print("WHAT WE JUST LEARNED: KNN")
print("=" * 60)

knn_example = """
Training Data (What we gave the algorithm):
┌─────────────┬──────────┬──────────────┐
│   Income    │  CIBIL   │  Loan Status │ ← LABEL (Answer!)
├─────────────┼──────────┼──────────────┤
│   ₹30,000   │   650    │   Approved   │
│   ₹45,000   │   720    │   Approved   │
│   ₹25,000   │   490    │   Rejected   │
│   ₹60,000   │   800    │   Approved   │
└─────────────┴──────────┴──────────────┘

Algorithm learned: "Show me your neighbors, I'll tell your status"

This is SUPERVISED LEARNING! 
Why? Humne algorithm ko answers (labels) diye!
"""

print(knn_example)

# ============================================
# PART 2: The Big Picture - ML Categories
# ============================================

print("\n" + "=" * 60)
print("THE BIG PICTURE: Machine Learning Categories")
print("=" * 60)

ml_tree = """
                    Machine Learning
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   SUPERVISED      UNSUPERVISED      REINFORCEMENT
   (With Labels)   (No Labels)       (Learn by Trial)
        │                 │                 │
    ┌───┴───┐         ┌───┴───┐         (ChatGPT,
    │       │         │       │          Game AI,
Classification Regression Clustering Dimensionality  AlphaGo)
    │       │         │       │
   KNN    Linear   K-Means   PCA
 Logistic  Regression
"""

print(ml_tree)

# ============================================
# PART 3: Banking Examples (Relatable!)
# ============================================

print("\n" + "=" * 60)
print("BANKING EXAMPLES - Same Domain, Different Learning")
print("=" * 60)

banking_examples = """
🏦 Bajaj Finance Use Cases:

1. SUPERVISED LEARNING (We have answers)
   ────────────────────────────────────
   Problem: Will customer default on loan?
   Data:    Income, CIBIL, Age, Employment → DEFAULT (Yes/No)
   
   Examples:
   ✓ Loan Approval (Approved/Rejected) ← KNN jo tumne sikha!
   ✓ Credit Card Fraud (Fraud/Not Fraud)
   ✓ Customer Churn (Will Leave/Will Stay)
   ✓ EMI Default Prediction (Will Pay/Won't Pay)

2. UNSUPERVISED LEARNING (No answers given!)
   ──────────────────────────────────────────
   Problem: Group similar customers together
   Data:    Income, CIBIL, Age, Spending → NO LABEL!
   
   Examples:
   ✓ Customer Segmentation (Find groups automatically)
     - High income, low spending (Savers)
     - Medium income, high spending (Impulse buyers)
     - Low income, low CIBIL (High risk)
   
   ✓ Fraud Pattern Detection (Find unusual transactions)
   ✓ Product Recommendation (Find similar customers)

3. REINFORCEMENT LEARNING (Learn by doing)
   ────────────────────────────────────────
   Problem: Optimize loan offers over time
   
   Examples:
   ✓ Dynamic Interest Rates (Learn what works)
   ✓ Personalized Loan Offers (Maximize approvals)
   ✓ Collections Strategy (When to call, what to offer)
"""

print(banking_examples)

# ============================================
# PART 4: The KEY Difference (Visual)
# ============================================

print("\n" + "=" * 60)
print("THE KEY DIFFERENCE")
print("=" * 60)

key_diff = """
SUPERVISED vs UNSUPERVISED - Same Data, Different Questions!

Dataset: Bajaj Finance Customers
┌─────────┬────────┬─────┬─────────────┐
│ Income  │ CIBIL  │ Age │ Loan Status │
├─────────┼────────┼─────┼─────────────┤
│ 30,000  │  650   │ 28  │  Approved   │ ← SUPERVISED has this!
│ 45,000  │  720   │ 35  │  Approved   │
│ 25,000  │  490   │ 42  │  Rejected   │
└─────────┴────────┴─────┴─────────────┘


SUPERVISED Learning (Teacher mode 👨‍🏫)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Question: "New customer aaya, approve karein ya reject?"
Training: Algorithm ko past answers diye
Algorithm: "Maine dekha, jiske paas aise neighbors the, 
            unko approve kiya gaya tha, so APPROVED!"

Example: KNN, Logistic Regression, Decision Trees
Use Case: Prediction with known outcomes


UNSUPERVISED Learning (Self-learning mode 🤔)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Question: "Mere customers mein kaun kaun se groups hain?"
Training: NO LABELS! Algorithm ko data diya, patterns dhundne bola
Algorithm: "Maine dekha, 3 types ke customers hain:
            - Group 1: High income + High CIBIL (Premium)
            - Group 2: Medium income + Medium CIBIL (Standard)  
            - Group 3: Low income + Low CIBIL (Risky)"

Example: K-Means Clustering, PCA
Use Case: Pattern discovery, Grouping


ANALOGY 🎯
━━━━━━━━━
Supervised   = Exam with answer key
               (Learn from solved examples)

Unsupervised = Research project
               (Find patterns yourself, no answers given)
"""

print(key_diff)

# ============================================
# PART 5: Quick Decision Tree
# ============================================

print("\n" + "=" * 60)
print("HOW TO DECIDE? (Decision Flowchart)")
print("=" * 60)

decision_tree = """
Start Here: What data do you have?
│
├─ Do you have LABELED data (answers/outcomes)?
│  │
│  ├─ YES → SUPERVISED LEARNING
│  │  │
│  │  ├─ Output is Category (Yes/No, Approved/Rejected)?
│  │  │  └─ CLASSIFICATION (KNN, Logistic, Decision Tree)
│  │  │
│  │  └─ Output is Number (Price, Salary, Amount)?
│  │     └─ REGRESSION (Linear Regression, Random Forest)
│  │
│  └─ NO → UNSUPERVISED LEARNING
│     │
│     ├─ Want to find GROUPS?
│     │  └─ CLUSTERING (K-Means, DBSCAN)
│     │
│     └─ Want to reduce FEATURES?
│        └─ DIMENSIONALITY REDUCTION (PCA, t-SNE)


Real Examples:
━━━━━━━━━━━━━
✓ Spam Email Detection → Supervised (Classification)
✓ House Price Prediction → Supervised (Regression)
✓ Customer Segmentation → Unsupervised (Clustering)
✓ Recommendation System → Can be both!
✓ Fraud Detection → Often starts Unsupervised, then Supervised
"""

print(decision_tree)

# ============================================
# PART 6: Interactive Exercise
# ============================================

print("\n" + "=" * 60)
print("LET'S PRACTICE! (Ask Students)")
print("=" * 60)

quiz = """
Given these scenarios, is it Supervised or Unsupervised?

1. Netflix: "Find groups of users with similar watching habits"
   Answer: ?

2. Amazon: "Will this customer buy this product? (Yes/No)"
   Answer: ?

3. Bank: "Predict customer's credit score (300-900)"
   Answer: ?

4. Zomato: "Group restaurants by cuisine type" (no labels given)
   Answer: ?

5. Flipkart: "Is this review POSITIVE or NEGATIVE?"
   Answer: ?


ANSWERS:
1. Unsupervised (Clustering - no labels for "groups")
2. Supervised (Classification - Yes/No is the label)
3. Supervised (Regression - predicting a number)
4. Unsupervised (Clustering - finding patterns)
5. Supervised (Classification - Positive/Negative is the label)
"""

print(quiz)

# ============================================
# SUMMARY
# ============================================

print("\n" + "=" * 60)
print("KEY TAKEAWAYS 🎯")
print("=" * 60)

summary = """
1. SUPERVISED = You have answers (labels)
   - Algorithm learns from examples with correct answers
   - Used for: Prediction, Classification, Regression
   - KNN (jo tumne abhi seekha) is SUPERVISED!

2. UNSUPERVISED = No answers given
   - Algorithm finds patterns on its own
   - Used for: Grouping, Pattern discovery
   - Example: Customer segmentation

3. The BIG question:
   "Do I have labels in my data?"
   YES → Supervised
   NO  → Unsupervised

4. Real ML projects often use BOTH:
   - Start with Unsupervised (find patterns)
   - Then use Supervised (make predictions)
"""

print(summary)
print("\n" + "=" * 60)