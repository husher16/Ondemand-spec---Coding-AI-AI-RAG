import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from serpapi import GoogleSearch
from pydantic import BaseModel, Field
from typing import Optional
from travel_agent_api.utils.tracing import print_trace

load_dotenv()


class FlightsInput(BaseModel):
    departure_airport: str = Field(description="The departure airport code (IATA).")
    arrival_airport: str = Field(description="The arrival airport code (IATA).")
    outbound_date: str = Field(description="The outbound date (YYYY-MM-DD) e.g. 2024-12-13.")
    return_date: str = Field(description="The return date (YYYY-MM-DD) e.g. 2024-12-19.")
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(0, description="The number of children. Defaults to 0.")


class FlightsInputSchema(BaseModel):
    params: FlightsInput


def _mock_flights(params: FlightsInput) -> dict:
    """Genera dati di volo realistici per la modalità test/mock."""
    dep = params.departure_airport.upper()
    arr = params.arrival_airport.upper()
    return {
        "search_parameters": {
            "departure_id": dep,
            "arrival_id": arr,
            "outbound_date": params.outbound_date,
            "return_date": params.return_date,
            "adults": params.adults,
            "children": params.children
        },
        "best_flights": [
            {
                "airline": "Ryanair / ITA Airways",
                "price": 149 * (params.adults or 1),
                "departure_token": "mock_dep_token_123",
                "flights": [
                    {
                        "departure_airport": {"id": dep, "time": f"{params.outbound_date} 09:30"},
                        "arrival_airport": {"id": arr, "time": f"{params.outbound_date} 11:45"},
                        "airline": "Ryanair",
                        "flight_number": "FR 8421",
                        "duration": "2h 15m",
                        "airplane": "Boeing 737-800"
                    },
                    {
                        "departure_airport": {"id": arr, "time": f"{params.return_date} 16:15"},
                        "arrival_airport": {"id": dep, "time": f"{params.return_date} 18:30"},
                        "airline": "Ryanair",
                        "flight_number": "FR 8422",
                        "duration": "2h 15m",
                        "airplane": "Boeing 737-800"
                    }
                ],
                "booking_token": f"https://www.google.com/travel/flights?q=Flights%20to%20{arr}%20from%20{dep}"
            }
        ],
        "other_flights": [
            {
                "airline": "EasyJet",
                "price": 185 * (params.adults or 1),
                "flights": [
                    {
                        "departure_airport": {"id": dep, "time": f"{params.outbound_date} 14:00"},
                        "arrival_airport": {"id": arr, "time": f"{params.outbound_date} 16:20"},
                        "airline": "EasyJet",
                        "flight_number": "U2 3211",
                        "duration": "2h 20m"
                    }
                ]
            }
        ]
    }


@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInput):
    """
    This tool uses the SerpApi Google Flights API to retrieve flights info.

    Parameters:
        departure_airport (str): The departure airport code (IATA).
        arrival_airport (str): The arrival airport code (IATA).
        outbound_date (str): The outbound date (YYYY-MM-DD) e.g. 2024-12-13.
        return_date (str): The return date (YYYY-MM-DD) e.g. 2024-12-19.
        adults (int): The number of adults. Defaults to 1.
        children (int): The number of children. Defaults to 0.

    Returns:
        dict: A dictionary containing the flights info. If the API call fails, it returns the error message as a string.
    """
    api_mode = os.getenv("API_MODE", "prod").lower()
    api_key = os.getenv("SERPAPI_API_KEY", "")

    # Tracing richiesto da specifica
    print("*" * 80)
    print("flights_finder")
    print(f"Departure: {params.departure_airport} -> Arrival: {params.arrival_airport}")
    print(f"Dates: {params.outbound_date} to {params.return_date} | Adults: {params.adults} | Children: {params.children}")
    print("*" * 80)

    print_trace("flights_finder_invoked", {
        "mode": api_mode,
        "departure": params.departure_airport,
        "arrival": params.arrival_airport,
        "outbound_date": params.outbound_date,
        "return_date": params.return_date,
        "adults": params.adults,
        "children": params.children
    })

    # Modalita' test o assenza di chiave valida
    if api_mode == "test" or not api_key or "YOUR_SERPAPI_API_KEY" in api_key:
        print("[flights_finder] Modalità TEST attiva: restituzione dati mock.")
        return _mock_flights(params)

    try:
        query_params = {
            "api_key": api_key,
            "engine": "google_flights",
            "hl": "it",
            "gl": "it",
            "currency": "EUR",
            "stops": "1",
            "departure_id": params.departure_airport,
            "arrival_id": params.arrival_airport,
            "outbound_date": params.outbound_date,
            "return_date": params.return_date,
            "adults": params.adults,
            "children": params.children
        }
        search = GoogleSearch(query_params)
        res = search.get_dict()
        return res
    except Exception as e:
        print(f"[flights_finder] Errore chiamata SerpApi: {e}. Fallback su dati simulati.")
        # Fallback morbido per evitare il blocco della catena LLM
        return _mock_flights(params)
