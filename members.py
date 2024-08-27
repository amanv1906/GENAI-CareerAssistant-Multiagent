def get_team_members_details() -> dict:
    """
    Returns a dictionary containing details of team members.

    Each team member is represented as a dictionary with the following keys:
    - name: The name of the team member.
    - description: A brief description of the team member's role and responsibilities.

    Returns:
    A dictionary containing details of team members.
    """
    members_dict = [
        {
            "name": "ResumeAnalyzer",
            "description": "Responsible for analyzing resumes to extract key information.",
        },
        {
            "name": "CoverLetterGenerator",
            "description": "Specializes in creating and optimizing cover letters tailored to job descriptions. Highlights the candidate's strengths and ensures the cover letter aligns with the requirements of the position.",
        },
        {
            "name": "JobSearcher",
            "description": "Conducts job searches based on specified criteria such as industry, location, and job title.",
        },
        {
            "name": "WebResearcher",
            "description": "Conducts online research to gather information from web.",
        },
        {
            "name": "ChatBot",
            "description": "If user is asking something to format or he want to get some information from the messages."
        },
        {
            "name": "Finish",
            "description": "Represents the end of the workflow.",
        },
    ]
    return members_dict
