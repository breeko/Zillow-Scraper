from bs4 import BeautifulSoup
from utils.utils import clean_dict, add_time
import json

def get_attrs_from_html(browser):
    # setup 
    inner_html = browser.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(inner_html,"html.parser")
    data_elem = soup.find('script', id="hdpApolloPreloadedData")
    if not data_elem:
        return None
    data = json.loads(data_elem.text)
    if "ForSaleSEORenderQuery" not in data.keys():
        return None
    key = next(x for x in data.keys() if "ForSaleSEORenderQuery" in x)
    prop = data[key]["property"]

    attrs = {
        "price": prop.get("price"),
        "state": prop.get("state"),
        "city": prop.get("city"),
        "description": prop.get("description"),
        "beds": prop.get("bedrooms"),
        "baths": prop.get("bathrooms"),
        "sqft": prop.get("livingArea"),
        "zestimate": prop.get("zestimate"),
        "rent_zestimate": prop.get("rentZestimate"),
        "address": prop.get("streetAddress"),
        "zipcode": prop.get("zipcode"),
        "zpid": prop.get("zpid"),
        "home_type": prop.get("homeType"),
        "latitude": prop.get("latitude"),
        "longitude": prop.get("longitude"),
        "home_status": prop.get("homeStatus"),
        **get_school(prop, 1),
        **get_school(prop, 2),
        **get_school(prop, 3),
        "facts": get_facts(prop)
    }
    attrs = clean_dict(attrs)
    attrs = add_time(attrs)
    return attrs

def get_facts(prop):
    if not prop.get("homeFacts") or not prop["homeFacts"].get("categoryDetails"):
        return None
    facts = []
    category_details = prop["homeFacts"]["categoryDetails"]
    for category_detail in category_details:
        categories = category_detail.get("categories", [])
        for category in categories:
            category_facts = category.get("categoryFacts", [])
            for category_fact in category_facts:
                fact_label = category_fact.get("factLabel")
                fact_value = category_fact.get("factValue")
                if fact_label:
                    facts.append("{}: {}".format(fact_label, fact_value))
                else:
                    facts.append("{}".format(fact_value))
    return ";".join(facts)

def get_school(prop, num_school):
    if not prop.get("schools") or len(prop["schools"]) < num_school:
        return {}
    idx_school = num_school - 1
    out = {
        "name": prop["schools"][idx_school].get("name"),
        "grades": prop["schools"][idx_school].get("grades"),
        "rating": prop["schools"][idx_school].get("rating"),
        "distance": prop["schools"][idx_school].get("distance"),
        "students_per_teacher": prop["schools"][idx_school].get("studentsPerTeacher"),
        "link": prop["schools"][idx_school].get("link"),
        "size": prop["schools"][idx_school].get("size"),
        "level": prop["schools"][idx_school].get("level")
    }
    out = {"school_{}_{}".format(num_school, k): v for k, v in out.items()}
    return out
