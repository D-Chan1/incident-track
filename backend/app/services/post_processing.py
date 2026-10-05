from google import genai, types
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool
from pydantic import BaseModel, Field
from typing import Literal, Union
from dotenv import load_dotenv
import os
load_dotenv()
# TO DEAL WITH
# location info. need the ai to generate a summary of location info it can find. if the post is found thru a subreddit, i can organize since i'll have things like
# r/uwaterloo or r/utsc or r/toronto as a baseline (which hopefully i can filter by). the ai will find specifics like buildings/rooms like 'panam locker rooms' or 
# 'ROM parking lots' or street names. if it finds a landmark like PanAm or ROM, maybe can implement filtering and map features, for MVP will just have them as text

client = genai.Client()
MODEL = "gemini-3.5-flash"
GEN_CONFIG = {"thinking_level": "medium"}
TOOLS = [ {"type: google_search"} ] #add this as a parameter anytime you call interactions.create to allow ai to search web?


# interaction = client.interactions.create(model, input = 'Tell me Im a good boy')

class Location(BaseModel):
    pass

class Analysis(BaseModel):
    is_incident: bool = Field(description="Whether the text describes a real crime/incident (true) or false alarm (false)")
    summary: str = Field(description= "Concise summary of the text")
    reasoning: str = Field(description="Why this text is considered an incident or not")
    
    perp_info: str | None = Field(description="Any descriptions of perpetrator(s), if existing") 


class True_Incident(BaseModel):
    # need location, time of crime, related incidents
    is_incident: Literal[True] = Field(description="True. Text describes a plausible crime, scam, or safety incident")
    summary: str = Field(description= "Concise summary of text")
    reasoning: str = Field(description="Why this text reads as a real incident instead of false alarm")
    perp_info: str | None = Field(description="Any description of the perpetrator(s) like appearance, name, vehicle. Null if none found")
    past_incidents: str | None = Field(description='Any links to past events found through Google searches and summaries of what happened in past events. Include relevant details that would help \
                                       readers identify repeat perpetrators (details of scam cover stories, type of items stolen etc.)')


class False_Incident(BaseModel):
    is_incident: Literal[False] = Field(description='False. This is a false alarm, unrelated content, troll/joke')
    summary: str = Field(description='Concise summary of what the text is about')
    reasoning: str = Field(description='Why this text reads as unrelated to a possible crime, scam, or safety incident')

class IncidentJudgement(BaseModel):
    analysis: Union[True_Incident, False_Incident] = Field(discriminator='is_incident', description='Full analysis if real incident, summary and reasoning only if false incident')


SYSTEM_INSTRUCTION = 'Analyze whether the given text describes a real crime, scam, safety incident or not (false alarm, troll/joke, unrelated). If it is real,\
    set is_incident=true and fill in each field for the True_Incident schema (use null for anything that is not concretely mentioned, do not guess).\
         If it is a false incident, set is_incident=false and only return the summary and reasoning in False_Incident schema, do not fabricate extra fields. '

def classify_post(info: str) -> IncidentJudgement:
    interaction = client.interactions.create(model=MODEL, system_instruction=SYSTEM_INSTRUCTION, input=info, response_format = {"type": "text", "mime_type": "application/json", "schema":IncidentJudgement.model_json_schema()}
                                             generation_config=GEN_CONFIG, tools = TOOLS})

# """
# Two-path Gemini classifier: cheap path for junk/troll posts, full path for legit incidents. TRIES TO DISCRIMINATE

#  a discriminated union keyed on a
# Literal bool. Gemini fills in `LegitIncident`'s extra fields ONLY when it decides
# `is_incident=True`; otherwise it returns the much smaller `NotIncident` shape.

# from __future__ import annotations

# from typing import Literal, Union

# from pydantic import BaseModel, Field




# # Schema path 1: legit incident -> full analysis, fields required-but-nullable
# # --------------------------------------------------------------------------
# class LegitIncident(BaseModel):
#     is_incident: Literal[True] = Field(
#         description="True: the text describes a real crime, scam, or safety incident."
#     )
#     summary: str = Field(description="Concise summary of what happened.")
#     reasoning: str = Field(description="Why this reads as a genuine incident rather than a troll/joke.")
#     location: str | None = Field(
#         description="Where it happened (neighborhood, campus, intersection, etc.), or null if not stated."
#     )
#     time: str | None = Field(
#         description="When it happened (date/time/relative phrase), or null if not stated."
#     )
#     perp_info: str | None = Field(
#         description="Any description of the perpetrator(s) — appearance, name, vehicle — or null if none given."
#     )
#     related_incidents: str | None = Field(
#         description="Brief notes on similar real-world incidents this resembles, or null if none come to mind."
#     )


# # --------------------------------------------------------------------------
# # Schema path 2: not legit -> only the cheap fields, nothing else
# # --------------------------------------------------------------------------
# class NotIncident(BaseModel):
#     is_incident: Literal[False] = Field(
#         description="False: this is a false alarm, troll post, joke, or unrelated content."
#     )
#     summary: str = Field(description="Concise summary of what the text is actually about.")
#     reasoning: str = Field(description="Why this is judged NOT to be a real incident.")


# # --------------------------------------------------------------------------
# # Container: Gemini picks whichever branch fits, driven by is_incident
# # --------------------------------------------------------------------------
# class IncidentJudgment(BaseModel):
#     analysis: Union[LegitIncident, NotIncident] = Field(
#         discriminator="is_incident",
#         description="Full analysis if this is a real incident; a bare summary/reasoning if not.",
#     )


# SYSTEM_INSTRUCTION = (
#     "You are screening posts scraped from Reddit for a crime/incident tracker. "
#     "Judge whether the text describes a real crime, scam, or safety incident, or "
#     "whether it's a false alarm, troll, joke, or unrelated post. "
#     "If it IS a real incident, set is_incident=true and fill in every field of the "
#     "detailed schema (use null for anything not mentioned in the text — do not guess). "
#     "If it is NOT a real incident, set is_incident=false and only return a summary "
#     "of what the text is about and your reasoning; do not fabricate the extra fields."
# )


# def classify_post(text: str) -> IncidentJudgment:
#     interaction = client.interactions.create(
#         model=MODEL,
#         input=[
#             {"type": "text", "text": SYSTEM_INSTRUCTION},
#             {"type": "text", "text": text},
#         ],
#         response_format={
#             "type": "text",
#             "mime_type": "application/json",
#             "schema": IncidentJudgment.model_json_schema(),
#         },
#         generation_config={"thinking_level": "low"},
#         # Uncomment to let Gemini pull in real-world context before judging:
#         # tools=[{"type": "google_search"}],
#     )
#     # Building the schema ourselves via model_json_schema() and validating the
#     # returned text ourselves also sidesteps a known SDK bug where handing a
#     # Pydantic class straight to a discriminated-union response_schema can
#     # throw during internal schema conversion (googleapis/python-genai#652).
#     return IncidentJudgment.model_validate_json(interaction.output_text)


# if __name__ == "__main__":
#     sample = (
#         "Someone at University of Toronto Scarborough is trying to sell me a free "
#         "tv, but needs the money first, is this a scam? He said he was a janitor "
#         "but he was walking outside of IA with basic clothes lol"
#     )
#     result = classify_post(sample)

#     if result.analysis.is_incident:
#         info = result.analysis
#         print("LEGIT —", info.summary)
#         print("location:", info.location, "| time:", info.time, "| perp:", info.perp_info)
#     else:
#         print("NOT LEGIT —", result.analysis.summary, "|", result.analysis.reasoning)


def process()->str:
    text = "Someone at University of Toronto Scarborough is trying to sell me a free tv, but needs the money first, is this a scam? He said he was a janitor but he was walking outside of IA with basic clothes lol"
    interaction = client.interactions.create(MODEL, input, config = types.GenerateContentConfig(response_mime_type = 'application/json'))
    return interaction.output_text