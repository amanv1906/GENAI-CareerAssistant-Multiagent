from typing import Any, TypedDict
from langchain.agents import (
    AgentExecutor,
    create_openai_tools_agent,
)
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from chains import get_finish_chain, get_supervisor_chain
from tools import (
    get_job_search_tool,
    ResumeExtractorTool,
    generate_letter_for_specific_job,
    get_google_search_results,
    save_cover_letter_for_specific_job,
    scrape_website,
)
from prompts import (
    get_search_agent_prompt_template,
    get_analyzer_agent_prompt_template,
    researcher_agent_prompt_template,
    get_generator_agent_prompt_template,
)

load_dotenv()


def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    """
    Creates an agent using the specified ChatOpenAI model, tools, and system prompt.

    Args:
        llm : LLM to be used to create the agent.
        tools (list): The list of tools to be given to the worker node.
        system_prompt (str): The system prompt to be used in the agent.

    Returns:
        AgentExecutor: The executor for the created agent.
    """
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


def supervisor_node(state):
    """
    The supervisor node is the main node in the graph. It is responsible for routing to the correct agent.
    """
    chat_history = state.get("messages", [])
    llm = init_chat_model(**state["config"])
    supervisor_chain = get_supervisor_chain(llm)
    if not chat_history:
        chat_history.append(HumanMessage(state["user_input"]))
    output = supervisor_chain.invoke({"messages": chat_history})
    state["next_step"] = output.next_action
    state["messages"] = chat_history
    return state


def job_search_node(state):
    """
    This Node is responsible for searching for jobs from linkedin or any other job search engine.
    Tools: Job Search Tool
    """
    llm = init_chat_model(**state["config"])
    search_agent = create_agent(
        llm, [get_job_search_tool()], get_search_agent_prompt_template()
    )
    chat_history = state.get("messages", [])
    state["callback"].write_agent_name("JobSearcher Agent 💼")
    output = search_agent.invoke(
        {"messages": chat_history}, {"callbacks": [state["callback"]]}
    )
    state["messages"].append(
        HumanMessage(content=output.get("output"), name="JobSearcher")
    )
    return state


def resume_analyzer_node(state):
    """
    Resume analyzer node will analyze the resume and return the output.
    Tools: Resume Extractor
    """
    llm = init_chat_model(**state["config"])
    analyzer_agent = create_agent(
        llm, [ResumeExtractorTool()], get_analyzer_agent_prompt_template()
    )
    state["callback"].write_agent_name("ResumeAnalyzer Agent 📄")
    output = analyzer_agent.invoke(
        {"messages": state["messages"]}, {"callbacks": [state["callback"]]}
    )
    state["messages"].append(
        HumanMessage(content=output.get("output"), name="ResumeAnalyzer")
    )
    return state


def cover_letter_generator_node(state):
    """
    Node which handles the generation of cover letters.
    Tools: Cover Letter Generator, Cover Letter Saver
    """
    llm = init_chat_model(**state["config"])
    generator_agent = create_agent(
        llm,
        [
            generate_letter_for_specific_job,
            save_cover_letter_for_specific_job,
            ResumeExtractorTool(),
        ],
        get_generator_agent_prompt_template(),
    )

    state["callback"].write_agent_name("CoverLetterGenerator Agent ✍️")
    output = generator_agent.invoke(
        {"messages": state["messages"]}, {"callbacks": [state["callback"]]}
    )
    state["messages"].append(
        HumanMessage(
            content=output.get("output"),
            name="CoverLetterGenerator",
        )
    )


def web_research_node(state):
    """
    Node which handles the web research.
    Tools: Google Search, Web Scraper
    """
    llm = init_chat_model(**state["config"])
    research_agent = create_agent(
        llm,
        [get_google_search_results, scrape_website],
        researcher_agent_prompt_template(),
    )
    state["callback"].write_agent_name("WebResearcher Agent 🔍")
    output = research_agent.invoke(
        {"messages": state["messages"]}, {"callbacks": [state["callback"]]}
    )
    state["messages"].append(
        HumanMessage(content=output.get("output"), name="WebResearcher")
    )
    return state


def chatbot_node(state):
    llm = init_chat_model(**state["config"])
    finish_chain = get_finish_chain(llm)
    state["callback"].write_agent_name("ChatBot Agent 🤖")
    output = finish_chain.invoke({"messages": state["messages"]})
    state["messages"].append(AIMessage(content=output.content, name="ChatBot"))
    return state


def define_graph():
    """
    Defines and returns a graph representing the workflow of job search agent.
    Returns:
        graph (StateGraph): The compiled graph representing the workflow.
    """
    workflow = StateGraph(AgentState)
    workflow.add_node("ResumeAnalyzer", resume_analyzer_node)
    workflow.add_node("JobSearcher", job_search_node)
    workflow.add_node("CoverLetterGenerator", cover_letter_generator_node)
    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("WebResearcher", web_research_node)
    workflow.add_node("ChatBot", chatbot_node)

    members = [
        "ResumeAnalyzer",
        "CoverLetterGenerator",
        "JobSearcher",
        "WebResearcher",
        "ChatBot",
    ]
    workflow.set_entry_point("Supervisor")

    for member in members:
        # We want our workers to ALWAYS "report back" to the supervisor when done
        workflow.add_edge(member, "Supervisor")

    conditional_map = {k: k for k in members}
    conditional_map["Finish"] = END

    workflow.add_conditional_edges(
        "Supervisor", lambda x: x["next_step"], conditional_map
    )

    graph = workflow.compile()
    return graph


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    user_input: str
    messages: list[BaseMessage]
    next_step: str
    config: dict
    callback: Any
