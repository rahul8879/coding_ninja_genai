from schema import CoTResult
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

print('working')

# step 0 : define your model
llm = ChatOpenAI(model='gpt-4o-mini')

# step 1 : define your parser
cot_parser = PydanticOutputParser(pydantic_object=CoTResult)

print(cot_parser.get_format_instructions())
# print(llm.invoke('hi').content)
# step 2 : cot prompt

COT_PROMPT = ChatPromptTemplate.from_messages([
    ('system', '''Expert support email classifier.

Rules:
- Login broken after payment → Billing (NOT Technical)
- App crashes → Technical
- Pricing + evaluating alternatives → Churn Risk
- Feature requests → Feature Request
- Spam → Spam

Think step by step before classifying.

{format_instructions}'''),
    ('human', 'Subject: {subject}\nBody: {body}')
]).partial(format_instructions=cot_parser.get_format_instructions())


# step 3 : define your lcel or chain
chain = COT_PROMPT | llm | cot_parser

# call your chain 
# email = {
#     'subject': "Can't login — paid for annual plan last week",
#     'body': 'Our entire team cannot login. We paid for the annual plan '
#             'last week. We have a board demo in 3 hours!'
# }

# print(chain.invoke(email))