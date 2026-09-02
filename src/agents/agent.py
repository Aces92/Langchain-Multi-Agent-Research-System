from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_website
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model= "openai/gpt-oss-20b",
    temperature=0,
    )

#1st search agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools= [web_search],
    )

#2nd reader agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_website],
        system_prompt="""
You are a research reader agent.

Your job is to select relevant sources from the search
results and scrape them for detailed information.

When scraping a URL:

- If the scraping succeeds, use the scraped content.
- If the scraping fails or returns an error, do not use
  the error as research.
- Try another relevant URL from the search results.
- Prefer reliable and relevant sources.
- Stop once you successfully obtain useful content.
- Return the useful scraped content to the next stage.
"""
    )



#writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """write a detailed research report on the topic below.


Topic: {topic}

Research Gathered:
{research}


Structure the report as:
- Introduction
-Key Findings (minimum 3 well-explained points)
-Conclusion
-Sources(list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


#critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific"),
    ("human", """Review the research report below and evaluate it strictly,
    
Report:
{report}

Respond in this exact format:

score: x/10

strengths:
- ...
- ...

Areas to improve:

- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()