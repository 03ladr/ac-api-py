# IPFS connectivity
import ipfshttpclient

# Utilities
import json

# Local modules
from .. import item_objects

# Item NFT Metadata
attribute = """{{\n\t    "trait_type": "{attr}",\n\t    "value": "{value}"\n\t}},"""
item_metadata = """{{
    "attributes": [
        {{
            "trait_type": "brand",
            "value": "{brand_name}"
        }},
        {{
            "trait_type": "lister",
            "value": "{listed_by}"
        }},
        {{
            "trait_type": "date",
            "value": "{current_date}"
        }},
        {attr1}
        {attr2}
        {attr3}
    ],
    "description": "{{}}",
    "image": "{{}}",
    "name": "{{}}"
}}"""


# Formats and uploads NFT metadata to IPFS from an Item object
def create_metadata(item: item_objects.ItemCreate):
    # Connecting to IPFS
    try:
        ipfs = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")
    except ipfshttpclient.exceptions.ConnectionError as ConnectionError:
        print(str(ConnectionError))

    # Formatting NFT Metadata
    item = item_metadata.format(
        brand_name=item.brand,
        listed_by=item.lister,
        current_date=item.date,
        attr1=attribute.format(
            attr=item.attributes.a1.trait_type, value=item.attributes.a1.value
        ),
        attr2=attribute.format(
            attr=item.attributes.a2.trait_type, value=item.attributes.a2.value
        ),
        attr3=attribute.format(
            attr=item.attributes.a3.trait_type, value=item.attributes.a3.value
        )[:-1],
        description=item.description,
        image=item.image,
        name=item.name,
    )

    # Loading NFT Metadata as a JSON object and cleaning
    item_json = json.loads(item)
    indexes = [
        i
        for i in range(len(item_json.get("attributes")))
        if item_json.get("attributes")[i]["trait_type"] == "None"
    ]
    for index in sorted(indexes, reverse=True):
        del item_json["attributes"][index]

    ipfs_metadata = ipfs.add_json(item_json)

    return "http://127.0.0.1:8080/ipfs/{cid}".format(cid=ipfs_metadata)
