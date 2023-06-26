import sys
import logging
import datetime
import os
from py_jama_rest_client.client import JamaClient, APIException

#######--CONFIG--#######
username = "exampleUsername"
password = "examplePassword"
client_id = "yourClientId"
client_secret = "yourClientSecret"
base_url = "https://yourBaseUrl"
project_id = 123                                                   # project ID to modify relationship types in
oauth = True

# follow the examples below to convert relationships between other itemTypes in Jama

# example of converting all 'Related to' relationships between requirements (upstream) and texts (downstream) into
# 'Verified By' relationships
epicToFeature = {}
epicToFeature.__setitem__("from_item_type_id", "24")                 # requirement itemType ID
epicToFeature.__setitem__("to_item_type_id", "33")                   # text itemType ID
epicToFeature.__setitem__("old_relationship_type", "Related to")        # old relationship name
epicToFeature.__setitem__("new_relationship_type", "Verified By")   # new relationship name

# example of converting all 'Related to' relationships between features (upstream) and stories (downstream) into
# 'Feature to Story' relationships
testcaseToRequirement = {}
testcaseToRequirement.__setitem__("from_item_type_id", "26")                # test case itemType ID
testcaseToRequirement.__setitem__("to_item_type_id", "24")                  # requirement itemType ID
testcaseToRequirement.__setitem__("old_relationship_type", "Related to")       # old relationship name
testcaseToRequirement.__setitem__("new_relationship_type", "Caused by")  # new relationship name

#####--END CONFIG--#####

logger = logging.getLogger(__name__)


def init_logging():
    try:
        os.makedirs('logs')
    except FileExistsError:
        pass
    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    log_file = 'logs/harm-severity-updater_' + str(current_date_time) + '.log'
    logging.basicConfig(filename=log_file, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def main():
    convert(epicToFeature)
    convert(testcaseToRequirement)


def create_jama_client():
    credentials = (username, password)
    if oauth:
        credentials = (client_id, client_secret)

    global jama_client
    jama_client = JamaClient(host_domain=base_url, credentials=credentials, oauth=oauth)


def convert(conversion_mapping):

    new_relationship_type_id = get_relationship_type_id(conversion_mapping.get("new_relationship_type"))
    if conversion_mapping.get("old_relationship_type") == "Any":
        old_relationship_type_id = -1
    else:
        old_relationship_type_id = get_relationship_type_id(conversion_mapping.get("old_relationship_type"))
    get_items_of_type(project_id,
                      conversion_mapping.get("from_item_type_id"),
                      conversion_mapping.get("to_item_type_id"),
                      new_relationship_type_id,
                      old_relationship_type_id)


def get_relationship_type_id(type_name):
    relationship_types = jama_client.get_relationship_types()
    for relationship_type in relationship_types:
        if relationship_type["name"] == type_name:
            return relationship_type["id"]

    print("Unable to locate relationship type: " + str(type_name))
    sys.exit(1)


def get_items_of_type(project_id, from_type, to_type, new_type, old_type):
    successes = 0
    attempts = 0

    print("Checking items:")

    items = jama_client.get_abstract_items(project=[project_id], item_type=[int(from_type)])

    for item in items:
        try:
            attempts += 1
            sys.stdout.write("\r{0} / {1}".format(attempts, len(items)))
            sys.stdout.flush()
            successes += evaluate_relationships(jama_client, project_id, item, to_type, old_type, new_type)
        except APIException as err:
            logger.error(msg="Unable to process item {}.".format(item))

    print("\nSuccessfully updated {0} relationships".format(successes))


def evaluate_relationships(jama_client, project_id, from_item, to_type, old_type, new_type):
    relationships = jama_client.get_relationships(project_id)
    successes = 0

    for relationship in relationships:
        try:
            to_item = relationship["toItem"]
            relationship_type = relationship["relationshipType"]
            if relationship_type != new_type and is_item_of_type(to_item, int(to_type)):
                if old_type == -1 or old_type == relationship_type:
                    print("\nUpdating relationship " + str(relationship["id"]) + " from relationshipType " + str(
                        old_type) + " to relationshipType " + str(new_type))
                    successes += update_relationship(relationship["id"], from_item, to_item, new_type)
        except APIException as err:
            logger.error(msg="Unable to process relationship {}.".format(relationship["id"]))
            logger.error(msg=str(err))

    return successes


def is_item_of_type(item_id, type_id):
    item = jama_client.get_item(item_id)
    return type_id == int(item["itemType"])


def update_relationship(relationship_id, from_item, to_item, relationship_type):
    try:
        jama_client.put_relationship(relationship_id=relationship_id, from_item=from_item["id"], to_item=to_item,
                                     relationship_type=relationship_type)
        return 1
    except APIException as err:
        logger.error(msg="Unable to update relationship {}".format(relationship_id))
        logger.error(msg=str(err))
        return 0


if __name__ == '__main__':
    init_logging()
    create_jama_client()
    main()
