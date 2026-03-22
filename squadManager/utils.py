from .rickmorty_client import RickMortyClient
import requests


def enrich_squad_members(members):
    """
    Enriches the list of squad members with detailed data from the Rick & Morty API.
    Makes requests to fetch information such as Name, Image, Species, Status, etc.
    """
    client = RickMortyClient()
    character_ids = [m.character_id for m in members]

    try:
        characters_by_id = client.get_characters(character_ids)
        return [
            {
                "member": member,
                "character": characters_by_id.get(member.character_id),
            }
            for member in members
        ]
    except requests.RequestException:
        # Case API error, return without data
        return [
            {
                "member": member,
                "character": None,
            }
            for member in members
        ]