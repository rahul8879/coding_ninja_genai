"""
UNSUPERVISED LEARNING - Super Simple Examples for Beginners
No complex terms, only relatable scenarios!
"""

print("=" * 70)
print("UNSUPERVISED LEARNING - Explained Like You're 5! 👶")
print("=" * 70)

# ============================================
# Example 1: School Students (Most Relatable!)
# ============================================

print("\n📚 Example 1: GROUPING STUDENTS IN CLASS")
print("-" * 70)

school_example = """
Scenario: Teacher ne class mein 30 students ko dekha

Data Available:
┌──────────┬─────────────┬──────────────┐
│   Name   │ Study Hours │ Sports Hours │
├──────────┼─────────────┼──────────────┤
│  Rahul   │      8      │      1       │
│  Priya   │      2      │      6       │
│  Amit    │      7      │      2       │
│  Sneha   │      3      │      5       │
│  Rohan   │      1      │      7       │
└──────────┴─────────────┴──────────────┘

❌ NO LABEL column! (Teacher didn't say "yeh topper hai", "yeh sports kid hai")

🤔 Algorithm's Job: Find natural groups!

Algorithm Found 3 Groups:
━━━━━━━━━━━━━━━━━━━━━━━━
Group 1: Studious Kids 📚
  - High study hours (7-9 hrs)
  - Low sports (0-2 hrs)
  - Examples: Rahul, Amit

Group 2: Sports Kids ⚽
  - Low study hours (1-3 hrs)
  - High sports (5-8 hrs)
  - Examples: Priya, Sneha, Rohan

Group 3: Balanced Kids ⚖️
  - Medium study (4-6 hrs)
  - Medium sports (3-4 hrs)

✨ Magic: Nobody told algorithm "yeh studious hai" - it discovered patterns itself!
"""

print(school_example)

# ============================================
# Example 2: Fruit Shop (Visual!)
# ============================================

print("\n🍎 Example 2: SORTING FRUITS")
print("-" * 70)

fruit_example = """
Scenario: Shopkeeper ke paas mixed fruits hain

Data Available (Sabzi waala dekh raha hai):
┌─────────┬───────────┬────────┐
│  Size   │   Color   │ Shape  │
├─────────┼───────────┼────────┤
│  Small  │    Red    │ Round  │
│  Large  │  Yellow   │  Long  │
│  Small  │    Red    │ Round  │
│ Medium  │  Orange   │ Round  │
│  Large  │  Yellow   │  Long  │
└─────────┴───────────┴────────┘

❌ NO LABEL! (Shopkeeper ne nahi bataya "yeh apple hai", "yeh banana hai")

Algorithm Found Groups:
━━━━━━━━━━━━━━━━━━━━━━
Basket 1: Small, Red, Round → Probably Apples 🍎
Basket 2: Large, Yellow, Long → Probably Bananas 🍌  
Basket 3: Medium, Orange, Round → Probably Oranges 🍊

✨ Algorithm ne khud groups banaye based on similarity!

Real Life Use:
- Photo gallery: Auto-group by faces, places, things
- Music app: Auto-create playlists by mood/genre
"""

print(fruit_example)

# ============================================
# Example 3: Your WhatsApp Contacts (Personal!)
# ============================================

print("\n📱 Example 3: WHATSAPP CONTACTS GROUPING")
print("-" * 70)

whatsapp_example = """
Scenario: Tumhare phone mein 200 contacts hain

Data Available (Phone dekh raha hai):
┌──────────────┬──────────────┬──────────────┐
│  Call Freq   │  Chat Freq   │  Time (AM/PM)│
├──────────────┼──────────────┼──────────────┤
│   Daily      │    Daily     │   Anytime    │  
│   Never      │    Rarely    │      -       │
│   Weekly     │    Daily     │   Night      │
│   Monthly    │    Monthly   │   Office hrs │
└──────────────┴──────────────┴──────────────┘

❌ NO LABEL! (You didn't tag "Family", "Work", "Friends")

Phone's Algorithm Creates Groups:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Group 1: Close Circle 💚
  - Talk daily
  - Chat daily  
  - Any time
  → Probably: Family, Best Friends

Group 2: Work People 💼
  - Talk weekly
  - Chat during office hours
  - Weekday only
  → Probably: Colleagues, Boss

Group 3: Occasional 👋
  - Talk monthly/never
  - Rare chats
  → Probably: Old friends, Acquaintances

Group 4: Night Owls 🌙
  - Chat at night
  - Daily messages
  → Probably: College friends, Gaming buddies

✨ Phone didn't ask you to label - it found patterns automatically!
"""

print(whatsapp_example)

# ============================================
# Example 4: YouTube (They Use Daily!)
# ============================================

print("\n🎥 Example 4: YOUTUBE VIDEO RECOMMENDATIONS")
print("-" * 70)

youtube_example = """
Scenario: YouTube has millions of videos

Your Watch History:
┌─────────────────────────────┬──────────┬────────────┐
│         Video Title         │ Duration │ Completed? │
├─────────────────────────────┼──────────┼────────────┤
│ Python Tutorial Part 1      │  20 min  │    Yes     │
│ Cricket Highlights IPL      │  15 min  │    Yes     │
│ Cooking Pasta Recipe        │  10 min  │    No      │
│ Python Tutorial Part 2      │  25 min  │    Yes     │
│ Football Skills             │  12 min  │    Yes     │
│ Machine Learning Basics     │  30 min  │    Yes     │
└─────────────────────────────┴──────────┴────────────┘

❌ NO LABELS! (You didn't tell YouTube "I like tech" or "I like sports")

YouTube's Algorithm Finds:
━━━━━━━━━━━━━━━━━━━━━━━━━━
Your Interest Groups:
1. Tech/Programming 💻 (watched fully, long videos)
2. Sports ⚽ (watched fully, medium videos)  
3. Cooking 🍳 (skipped - not interested)

Then Recommends:
✓ More Python tutorials (you watched similar)
✓ More sports highlights (you watched similar)
✗ No more cooking videos (you skipped)

✨ YouTube learned YOUR preferences without you explicitly saying anything!
"""

print(youtube_example)

# ============================================
# Example 5: Banking (Same Domain, Simple!)
# ============================================

print("\n🏦 Example 5: BANK CUSTOMERS (Simple Version)")
print("-" * 70)

simple_bank = """
Scenario: Bank has 1000 customers

Data Available:
┌─────────┬────────────┬──────────────┐
│ Salary  │  Spending  │ Savings/Month│
├─────────┼────────────┼──────────────┤
│ 30,000  │   25,000   │    5,000     │
│ 80,000  │   30,000   │   50,000     │
│ 50,000  │   55,000   │   -5,000     │
│ 90,000  │   40,000   │   50,000     │
│ 40,000  │   42,000   │   -2,000     │
└─────────┴────────────┴──────────────┘

❌ NO LABELS! (Bank didn't say "Premium", "Standard", "Risky")

Algorithm Discovers 3 Types:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type 1: SAVERS 💰
  - Good salary
  - Low spending  
  - High savings
  → Bank Insight: Offer them FD, Mutual Funds

Type 2: SPENDERS 🛍️
  - Medium/High salary
  - Very high spending
  - Negative savings (using credit!)
  → Bank Insight: Offer credit cards, loans

Type 3: STRUGGLERS 😰
  - Low salary
  - High spending
  - No savings
  → Bank Insight: Offer financial planning advice

✨ Bank found customer types without anyone telling them!

Real Use: 
- Send RIGHT offers to RIGHT people
- Premium credit card to Savers (they can afford it)
- Budget planning to Strugglers (they need it)
"""

print(simple_bank)

# ============================================
# THE BIG DIFFERENCE (Super Clear!)
# ============================================

print("\n" + "=" * 70)
print("🎯 THE DIFFERENCE (In Simple Words)")
print("=" * 70)

difference = """
SUPERVISED Learning = Learning with a Teacher 👨‍🏫
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Teacher shows examples:
  "Yeh apple hai" (points to apple)
  "Yeh banana hai" (points to banana)
  
Student learns patterns and then identifies new fruits correctly.

Example: Loan approval
  Data: Income, CIBIL → LABEL: Approved/Rejected ✅
  New customer → Predict: Approved or Rejected?


UNSUPERVISED Learning = Self Study 🤔
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No teacher! Just raw data:
  Here are 100 fruits (no names given)
  
Student groups them:
  "Yeh sab similar hain" (small, red, round together)
  "Yeh sab similar hain" (long, yellow together)
  
Discovers groups WITHOUT being told what they are!

Example: Customer segmentation
  Data: Income, Spending (NO LABELS ❌)
  Algorithm → Finds 3 groups automatically!


REAL WORLD COMBO 🎯
━━━━━━━━━━━━━━━━━
Step 1: Unsupervised (Find groups)
  "3 types ke customers mil gaye"

Step 2: Supervised (Make predictions)
  "Ab new customer aaye toh predict kar sakte hain which group"
"""

print(difference)

# ============================================
# EASY MEMORY TRICK
# ============================================

print("\n" + "=" * 70)
print("💡 EASY MEMORY TRICK")
print("=" * 70)

memory_trick = """
Question to Ask Yourself:
━━━━━━━━━━━━━━━━━━━━━━━━
"Kya mere paas ANSWER column hai?"

Examples:

1. "Income, CIBIL, Age, APPROVED/REJECTED" 
   → APPROVED/REJECTED is the ANSWER ✅
   → SUPERVISED!

2. "Income, CIBIL, Age" (that's it, no answer column)
   → No answer given ❌
   → UNSUPERVISED!


Another Way to Think:
━━━━━━━━━━━━━━━━━━━━
SUPERVISED   = Prediction karna hai
               (Will loan be approved? YES/NO)

UNSUPERVISED = Grouping karna hai
               (Kitne types ke customers hain?)


Real Examples:
━━━━━━━━━━━━
✓ Email: Spam or Not Spam? → SUPERVISED (we know answer)
✓ Group customers by behavior → UNSUPERVISED (find groups)
✓ Predict tomorrow's temperature → SUPERVISED (we have history)
✓ Find topics in news articles → UNSUPERVISED (discover topics)
"""

print(memory_trick)

print("\n" + "=" * 70)
print("🎓 END - Now You Understand Unsupervised Learning!")
print("=" * 70)