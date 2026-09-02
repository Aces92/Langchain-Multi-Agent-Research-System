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

You receive search results containing titles, URLs, and snippets.

Your job is to:
1. Read the search results.
2. Choose the most relevant URL.
3. Call the scrape_website tool using ONLY the URL.
4. The scrape_website tool requires this exact argument:
   {"url": "https://example.com"}
5. Do NOT pass query, topn, source, or any other arguments to scrape_website.
6. Do not perform another web search.
7. After scraping, return the useful information you obtained.
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