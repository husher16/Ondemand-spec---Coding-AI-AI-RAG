import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser
from travel_agent_api.utils.tracing import print_trace


class TravelPlanInput(BaseModel):
    start_date: str = Field(description="The start date of the trip (YYYY-MM-DD) e.g. 2024-12-13.")
    end_date: str = Field(description="The end date of the trip (YYYY-MM-DD) e.g. 2024-12-19.")
    destination: str = Field(description="The destination of the trip.")
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(0, description="The number of children. Defaults to 0.")
    travel_style: str = Field(description="The style of travel. e.g. adventure, relax, culture, backpacking, luxury, family-friendly.")
    budget: Optional[int] = Field(None, description="The total budget for the trip.")
    activities: str = Field(description="The preferred activities. e.g. culture, nature, food, shopping.")
    food_restriction: Optional[str] = Field(None, description="Any food restrictions. e.g. vegetarian, gluten-free.")


class TravelPlanInputSchema(BaseModel):
    params: TravelPlanInput


class TravelDayOutput(BaseModel):
    morning: str = Field(description="The activities for the morning.")
    afternoon: str = Field(description="The activities for the afternoon.")
    evening: str = Field(description="The activities for the evening.")


class TravelPlanOutput(BaseModel):
    travel_plan: list[TravelDayOutput]


def _mock_travel_plan(params: TravelPlanInput) -> TravelPlanOutput:
    """Piano di viaggio sintetico per test o fallback."""
    dest = params.destination
    return TravelPlanOutput(
        travel_plan=[
            TravelDayOutput(
                morning=f"🌅 Arrivo a {dest}, check-in e colazione tipica nel centro storico.",
                afternoon=f"🏛️ Visita culturale ai monumenti principali di {dest} ed esplorazione delle vie caratteristiche.",
                evening=f"🍷 Cena con specialità enogastronomiche locali in un ristorante tipico."
            ),
            TravelDayOutput(
                morning=f"☕ Tour guidato dei musei e delle meraviglie artistiche di {dest}.",
                afternoon=f"🛍️ Passeggiata nei quartieri iconici e tempo libero per shopping e relax.",
                evening=f"✨ Spettacolo serale, passeggiata al tramonto e degustazione di dolci tradizionali."
            )
        ]
    )


@tool(args_schema=TravelPlanInputSchema)
def chain_travel_plan(params: TravelPlanInput) -> TravelPlanOutput:
    """
    Generates a comprehensive travel plan based on user input parameters.

    Parameters:
        params (TravelPlanInput): The input parameters for the travel plan
        including dates, destination, number of travelers, travel style, budget,
        preferred activities, and any food restrictions.

    Returns:
        TravelPlanOutput: The generated travel plan content.
    """
    api_mode = os.getenv("API_MODE", "prod").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Tracing da specifica
    print("*" * 80)
    print("chain_travel_plan")
    print(f"Destination: {params.destination} | Dates: {params.start_date} to {params.end_date}")
    print(f"Style: {params.travel_style} | Budget: {params.budget} | Activities: {params.activities}")
    print("*" * 80)

    print_trace("chain_travel_plan_invoked", {
        "destination": params.destination,
        "dates": f"{params.start_date} - {params.end_date}",
        "travelers": f"{params.adults} adults, {params.children} children",
        "style": params.travel_style
    })

    if api_mode == "test" or not openai_key or "YOUR_OPENAI_API_KEY" in openai_key or "inserisci" in openai_key:
        print("[chain_travel_plan] Modalità TEST o chiave non configurata: restituzione piano mock.")
        return _mock_travel_plan(params)

    try:
        model = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
        output_parser = PydanticOutputParser(pydantic_object=TravelPlanOutput)

        system_prompt = f"""
You are a travel expert.
Your mission is to provide in-depth content on the topic to create a travel plan.
The start date of the trip is {params.start_date}.
The end date of the trip is {params.end_date}.
The destination of the trip is {params.destination}.
The number of adults is {params.adults}.
The number of children is {params.children}.
The style of travel is {params.travel_style}.
The total budget for the trip is {params.budget}.
The preferred activities are {params.activities}.
Any food restrictions are {params.food_restriction}
Use emojis to make your answers more engaging and friendly.
Always strive to be approachable and helpful, offering the
most accurate and useful information possible to users.

{output_parser.get_format_instructions()}
"""
        prompt = ChatPromptTemplate([("human", "{input}")])
        chain = prompt | model | output_parser
        result = chain.invoke({"input": system_prompt})
        return result
    except Exception as e:
        print(f"[chain_travel_plan] Errore esecuzione chain: {e}. Fallback su piano mock.")
        return _mock_travel_plan(params)
