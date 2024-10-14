from ast import List
from typing import Literal, Optional, List, Union
from pydantic import BaseModel, Field


class RouteSchema(BaseModel):
    next_action: Literal[
        "ResumeAnalyzer",
        "CoverLetterGenerator",
        "JobSearcher",
        "WebResearcher",
        "ChatBot",
        "Finish",
    ] = Field(
        ...,
        title="Next",
        description="Select the next role",
    )


class JobSearchInput(BaseModel):
    keywords: str = Field(
        description="Keywords describing the job role. (if the user is looking for a role in particular company then pass company with keywords)"
    )
    location_name: Optional[str] = Field(
        description='Name of the location to search within. Example: "Kyiv City, Ukraine".'
    )
    employment_type: Optional[
        List[
            Literal[
                "full-time",
                "contract",
                "part-time",
                "temporary",
                "internship",
                "volunteer",
                "other",
            ]
        ]
    ] = Field(description="Specific type(s) of job to search for.")
    limit: Optional[int] = Field(
        default=5, description="Maximum number of jobs to retrieve."
    )
    job_type: Optional[List[Literal["onsite", "remote", "hybrid"]]] = Field(
        description="Filter for remote jobs, onsite or hybrid"
    )
    experience: Optional[
        List[
            Literal[
                "internship",
                "entry-level",
                "associate",
                "mid-senior-level",
                "director",
                "executive",
            ]
        ]
    ] = Field(
        description='Filter by experience levels. Options are "internship", "entry level", "associate", "mid-senior level", "director", "executive". pass the exact arguments'
    )
    listed_at: Optional[Union[int, str]] = Field(
        default=86400,
        description="Maximum number of seconds passed since job posting. 86400 will filter job postings posted in the last 24 hours.",
    )
    distance: Optional[Union[int, str]] = Field(
        default=25,
        description="Maximum distance from location in miles. If not specified or 0, the default value of 25 miles is applied.",
    )
