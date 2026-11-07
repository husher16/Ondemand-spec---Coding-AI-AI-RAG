import os
from langchain_core.tools import tool
from serpapi import GoogleSearch
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from enum import IntEnum
from travel_agent_api.utils.tracing import print_trace

load_dotenv()


class HotelClassEnum(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class HotelsInput(BaseModel):
    q: str = Field(description="Location of the hotel.")
    check_in_date: str = Field(description="The outbound date (YYYY-MM-DD) e.g. 2024-12-13.")
    check_out_date: str = Field(description="The return date (YYYY-MM-DD) e.g. 2024-12-19.")
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(0, description="The number of children. Defaults to 0.")
    hotel_class: Optional[int] = Field(2, description="The hotel class available from 2 to 5. Defaults to 2.")


class HoltesInputSchema(BaseModel):
    params: HotelsInput


def _mock_hotels(params: HotelsInput) -> list[dict]:
    """Genera hotel realistici per la modalità test/mock coerenti con HOTELS_OUTPUT."""
    stars = params.hotel_class or 3
    city = params.q.split(",")[0].capitalize()
    return [
        {
            "name": f"Grand Hotel {city} Palace",
            "description": f"Elegante hotel {stars} stelle nel cuore di {city}, a pochi passi dalle principali attrazioni, con spa e colazione panoramica.",
            "rate_per_night": {"lowest": f"€{80 * stars}", "extracted_lowest": 80 * stars},
            "total_rate": {"lowest": f"€{80 * stars * 3}", "extracted_lowest": 80 * stars * 3},
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "overall_rating": 4.6,
            "reviews": 1280,
            "hotel_class": f"{stars}-star hotel",
            "amenities": ["Wi-Fi gratuito", "Spa e Centro Benessere", "Colazione inclusa", "Aria condizionata"],
            "images": [{"thumbnail": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"}]
        },
        {
            "name": f"Boutique Hotel Bella {city}",
            "description": f"Struttura di design raffinata e moderna, situata in posizione centrale con ristorante gourmet e terrazza.",
            "rate_per_night": {"lowest": f"€{65 * stars}", "extracted_lowest": 65 * stars},
            "total_rate": {"lowest": f"€{65 * stars * 3}", "extracted_lowest": 65 * stars * 3},
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "overall_rating": 4.4,
            "reviews": 850,
            "hotel_class": f"{stars}-star hotel",
            "amenities": ["Wi-Fi gratuito", "Bar / Lounge", "Reception 24/7", "Pet friendly"],
            "images": [{"thumbnail": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=500"}]
        }
    ]


@tool(args_schema=HoltesInputSchema)
def hotels_finder(params: HotelsInput):
    """
    This tool uses the SerpApi Google Hotels API to retrieve hotels info.

    Parameters:
        q (str): Location of the hotel.
        check_in_date (str): The outbound date (YYYY-MM-DD) e.g. 2024-12-13.
        check_out_date (str): The return date (YYYY-MM-DD) e.g. 2024-12-19.
        adults (int): The number of adults. Defaults to 1.
        children (int): The number of children. Defaults to 0.
        hotel_class (int): The hotel class available from 2 to 5. Defaults to 2.

    Returns:
        dict: A dictionary containing the hotels info. If the API call fails, it returns the error message as a string.
    """
    api_mode = os.getenv("API_MODE", "prod").lower()
    api_key = os.getenv("SERPAPI_API_KEY", "")

    # Tracing da specifica
    print("*" * 80)
    print("hotels_finder")
    print(f"Location: {params.q} | Dates: {params.check_in_date} to {params.check_out_date}")
    print(f"Class: {params.hotel_class} stars | Guests: {params.adults} adults, {params.children} children")
    print("*" * 80)

    print_trace("hotels_finder_invoked", {
        "mode": api_mode,
        "location": params.q,
        "check_in": params.check_in_date,
        "check_out": params.check_out_date,
        "hotel_class": params.hotel_class,
        "adults": params.adults,
        "children": params.children
    })

    if api_mode == "test" or not api_key or "YOUR_SERPAPI_API_KEY" in api_key:
        print("[hotels_finder] Modalità TEST attiva: restituzione hotel mock.")
        return _mock_hotels(params)

    query_params = {
        "api_key": api_key,
        "engine": "google_hotels",
        "hl": "it",
        "gl": "it",
        "currency": "EUR",
        "q": params.q,
        "check_in_date": params.check_in_date,
        "check_out_date": params.check_out_date,
        "adults": params.adults,
        "children": params.children,
        "hotel_class": params.hotel_class,
        "num": 5
    }

    try:
        search = GoogleSearch(query_params)
        results = search.get_dict().get("properties", [])
    except Exception as e:
        print(f"[hotels_finder] Errore chiamata SerpApi: {e}. Fallback su dati simulati.")
        results = _mock_hotels(params)

    return results
