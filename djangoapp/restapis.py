import requests
import json
from .models import CarDealer, DealerReview

from requests.auth import HTTPBasicAuth


def get_request(url, **kwargs):
    api_key = kwargs.get("api_key")
    params = kwargs.get("params", {})
    if api_key:
        response = requests.get(url, params=params, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
    else:
        response = requests.get(url, params=params)
    return response


def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result["rows"]
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   full_name=dealer_doc["full_name"], id=dealer_doc["id"],
                                   lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], st=dealer_doc["st"],
                                   zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results


def get_dealer_by_id(dealer_id):
    url = f"https://boratemayure-8000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp/dealers/{dealer_id}"  # Replace with the actual API URL
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        dealer_doc = json_result["doc"]
        dealer = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                            full_name=dealer_doc["full_name"], id=dealer_doc["id"],
                            lat=dealer_doc["lat"], long=dealer_doc["long"],
                            short_name=dealer_doc["short_name"], st=dealer_doc["st"],
                            zip=dealer_doc["zip"])
        return dealer
    return None


def get_dealers_by_state(state):
    url = f"https://boratemayure-8000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp/dealers?state={state}"  # Replace with the actual API URL
    json_result = get_request(url, state=state)
    results = []
    if json_result:
        dealers = json_result["rows"]
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   full_name=dealer_doc["full_name"], id=dealer_doc["id"],
                                   lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], st=dealer_doc["st"],
                                   zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        reviews = json_result["results"]
        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=review["sentiment"],
                id=review["id"]
            )
            results.append(review_obj)
    return results


def analyze_review_sentiments(dealerreview):
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/{instance_id}/v1/analyze"
    api_key = "vVosih1NmSES_31_VjfOXiT--gqR2_i5L6vlbm010Fzv"  # Replace with your actual API key
    version = "2021-03-25"
    features = "sentiment"
    return_analyzed_text = True

    params = {
        "text": dealerreview,
        "version": version,
        "features": features,
        "return_analyzed_text": return_analyzed_text
    }

    response = get_request(url, params=params, api_key=api_key)
    if response.status_code == 200:
        analyzed_data = response.json()
        sentiment = analyzed_data.get("sentiment", {}).get("document", {}).get("label")
        return sentiment
    else:
        return None

def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)
    return response