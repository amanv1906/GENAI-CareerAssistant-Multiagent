from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models.chat_models import BaseChatModel
from typing import List

from members import get_team_members_details
from prompts import get_supervisor_prompt_template, get_finish_step_prompt
from schemas import RouteSchema


def get_supervisor_chain(llm: BaseChatModel):
    """
    Returns a supervisor chain that manages a conversation between workers.

    The supervisor chain is responsible for managing a conversation between a group
    of workers. It prompts the supervisor to select the next worker to act, and
    each worker performs a task and responds with their results and status. The
    conversation continues until the supervisor decides to finish.

    Returns:
        supervisor_chain: A chain of prompts and functions that handle the conversation
                          between the supervisor and workers.
    """

    team_members = get_team_members_details()

    # Generate the formatted string
    formatted_string = ""
    for i, member in enumerate(team_members):
        formatted_string += (
            f"**{i+1} {member['name']}**\nRole: {member['description']}\n\n"
        )

    # Remove the trailing new line
    formatted_members_string = formatted_string.strip()
    system_prompt = get_supervisor_prompt_template()

    options = [member["name"] for member in team_members]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                """
                
                Few steps to follow:
                - Don't overcomplicate the conversation.
                - If the user asked something to search on web then get the information and show it.
                - If the user asked to analyze resume then just analyze it, don't be oversmart and do something else.
                - Don't call chatbot agent if user is not asking from the above conversation.
                
                Penalty point will be given if you are not following the above steps.
                Given the conversation above, who should act next?
                "Or should we FINISH? Select one of: {options}.
                 Do only what is asked, and do not deviate from the instructions. Don't hallucinate or 
                 make up information.""",
            ),
        ]
    ).partial(options=str(options), members=formatted_members_string)

    supervisor_chain = prompt | llm.with_structured_output(RouteSchema)

    return supervisor_chain


def get_finish_chain(llm: BaseChatModel):
    """
    If the supervisor decides to finish the conversation, this chain is executed.
    """
    system_prompt = get_finish_step_prompt()
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            ("system", system_prompt),
        ]
    )
    finish_chain = prompt | llm
    return finish_chain
