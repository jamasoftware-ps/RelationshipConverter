
#######--CONFIG--#######
username = "username"
password = "password"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
base_url = "{base_url}/rest/latest/"
project_id = 20183                                                      # project ID to modify relationship types in
oauth = True

# follow the examples below to convert relationships between other itemTypes in Jama

# example of converting all 'Related to' relationships between epics (upstream) and features (downstream) into
# 'Epic to Feature' relationships
epicToFeature = {}
epicToFeature.__setitem__("from_item_type_id", "89025")                 # epic itemType ID
epicToFeature.__setitem__("to_item_type_id", "89008")                   # feature itemType ID
epicToFeature.__setitem__("old_relationship_type", "Related to")        # old relationship name
epicToFeature.__setitem__("new_relationship_type", "Epic to Feature")   # new relationship name

# example of converting all 'Related to' relationships between features (upstream) and stories (downstream) into
# 'Feature to Story' relationships
featureToStory = {}
featureToStory.__setitem__("from_item_type_id", "89008")                # feature itemType ID
featureToStory.__setitem__("to_item_type_id", "89014")                  # story itemType ID
featureToStory.__setitem__("old_relationship_type", "Related to")       # old relationship name
featureToStory.__setitem__("new_relationship_type", "Feature to Story") # new relationship name

#####--END CONFIG--#####

import json
import sys
from py_jama_rest_client.client import JamaClient

def main():
    credentials = (username, password)
    if(oauth):
        credentials = (client_id, client_secret)

    global jama_client
    jama_client = JamaClient(credentials=credentials, oauth=oauth)

    convert(epicToFeature)
    convert(featureToStory)

def convert(conversionMapping):

    new_relationship_type_id = get_relationship_type_id(conversionMapping.get("new_relationship_type"))
    if conversionMapping.get("old_relationship_type") == "Any":
        old_relationship_type_id = -1
    else:
        old_relationship_type_id = get_relationship_type_id(conversionMapping.get("old_relationship_type"))
    get_items_of_type( project_id, 
                            conversionMapping.get("from_item_type_id"),
                            conversionMapping.get("to_item_type_id"),
                            new_relationship_type_id,
                            old_relationship_type_id)


def get_relationship_type_id(type_name):
    remaining_results = -1
    start_index = 0

    relationship_types = jama_client.get_relationship_types()
    for relationship_type in relationship_types:
        if relationship_type["name"] == type_name:
            return relationship_type["id"]

    print ("Unable to locate relationship type: " + str(type_name))
    sys.exit(1)

def get_items_of_type(project_id, from_type, to_type, new_type, old_type):
    successes = 0
    attempts = 0
    remaining_results = -1
    start_index = 0

    print("Checking items:")

    while remaining_results != 0:
        params = {
            "project": project_id,
            "itemType": from_type,
            "startAt": start_index
        }
        items = jama_client.get_items(params)

        page_info = items.meta.page_info
        total_results = page_info.total_results
        result_count = page_info.result_count
        remaining_results = total_results - (start_index + result_count)
        start_index += 20

        for item in items.data:
            attempts += 1
            sys.stdout.write("\r{0} / {1}".format(attempts, total_results))
            sys.stdout.flush()
            successes += evaluate_relationships(jama_client, project_id, item.id, to_type, old_type, new_type)

    print("Succesfully updated {0} relationships".format(successes))


def evaluate_relationships(project_id, from_item, to_type, old_type, new_type):
    successes = 0
    remaining_results = -1
    start_index = 0

    while remaining_results != 0:
        start_at = "startAt=" + str(start_index)

        relationships = jama_client.get_downstream_relationships(from_item, start_index=start_index)


        for relationship in relationships:
            to_item = relationship.to_item
            relationship_type = relationship.relationship_type
            if relationship_type != new_type and is_item_of_type(to_item, to_type):
                if old_type == -1 or old_type == relationship_type:
                    print("\nUpdating relationship " + str(relationship.id) + " from relationshipType " + str(
                        old_type) + " to relationshipType " + str(new_type))
                    successes += update_relationship(relationship.id, from_item, to_item, new_type)

        remaining_results = len(relationships)
        start_index += 20

    return successes


def is_item_of_type(item_id, type_id):
    url = base_url + "abstractitems/" + str(item_id)
    response = jama_client.get(url)
    if response.status_code >= 400:
        print (response.text)
    json_response = json.loads(response.text)
    returnValue = type_id == str(json_response["data"]["itemType"])
    return returnValue

def update_relationship(relationship_id, from_item, to_item, relationship_type):
    payload = {
        "fromItem": from_item,
        "toItem": to_item,
        "relationshipType": relationship_type
    }
    url = base_url + "relationships/" + str(relationship_id)
    response = jama_client.put(url, json=payload)
    if response.status_code >= 400:
        print (response.text)
        return 0
    return 1

