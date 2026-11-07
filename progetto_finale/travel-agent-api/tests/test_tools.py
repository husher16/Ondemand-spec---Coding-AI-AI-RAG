import os
import pytest
from travel_agent_api.tools.flights_finder import flights_finder, FlightsInput
from travel_agent_api.tools.hotels_finder import hotels_finder, HotelsInput
from travel_agent_api.tools.chain_historical_expert import chain_historical_expert
from travel_agent_api.tools.chain_travel_plan import chain_travel_plan, TravelPlanInput


def test_flights_finder_mock():
    os.environ["API_MODE"] = "test"
    params = FlightsInput(
        departure_airport="FCO",
        arrival_airport="CDG",
        outbound_date="2024-07-05",
        return_date="2024-07-12",
        adults=2,
        children=1
    )
    result = flights_finder.invoke({"params": params})
    assert isinstance(result, dict)
    assert "best_flights" in result or "search_parameters" in result


def test_hotels_finder_mock():
    os.environ["API_MODE"] = "test"
    params = HotelsInput(
        q="Roma",
        check_in_date="2024-05-15",
        check_out_date="2024-05-20",
        adults=2,
        children=0,
        hotel_class=4
    )
    result = hotels_finder.invoke({"params": params})
    assert isinstance(result, list)
    assert len(result) > 0
    assert "name" in result[0]


def test_historical_expert():
    os.environ["API_MODE"] = "test"
    result = chain_historical_expert.invoke({"input_text": "Storia del Colosseo a Roma"})
    assert isinstance(result, str)
    assert len(result) > 20


def test_travel_plan():
    os.environ["API_MODE"] = "test"
    params = TravelPlanInput(
        start_date="2024-06-15",
        end_date="2024-06-20",
        destination="Venezia",
        adults=2,
        children=0,
        travel_style="culture",
        budget=2000,
        activities="arte, musei",
        food_restriction="nessuna"
    )
    result = chain_travel_plan.invoke({"params": params})
    assert hasattr(result, "travel_plan")
    assert len(result.travel_plan) > 0
